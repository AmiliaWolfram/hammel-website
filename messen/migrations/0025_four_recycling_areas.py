"""Consolidate recycling areas into four categories while retaining machine assignments."""
from django.db import migrations, transaction

CANONICAL = [
    ('holz', 'Altholz & Grünabfälle'),
    ('muell', 'Gewerbe-, Industrie- & Hausmüll'),
    ('schrott', 'Metallrecycling'),
    ('spezial', 'Spezial Anwendung'),
]

@transaction.atomic
def forwards(apps, schema_editor):
    Area = apps.get_model('messen', 'RecyclingArea')
    Material = apps.get_model('messen', 'RecyclingMaterial')
    targets = {}
    for pos, (slug, title) in enumerate(CANONICAL, 1):
        area, _ = Area.objects.get_or_create(slug=slug, defaults={'title': title, 'position': pos})
        Area.objects.filter(pk=area.pk).update(title=title, position=pos)
        targets[slug] = area
    # Keep material primary keys and M2M relationships intact; disambiguate
    # identical names rather than deleting a material or a machine assignment.
    for source_slug in ('bauschutt', 'kunststoff'):
        source = Area.objects.filter(slug=source_slug).first()
        if source is None or source.pk == targets['spezial'].pk:
            continue
        for material in Material.objects.filter(area_id=source.pk).order_by('pk'):
            name = material.name
            if Material.objects.filter(area=targets['spezial'], name=name).exclude(pk=material.pk).exists():
                suffix = ' (Bauschutt)' if source_slug == 'bauschutt' else ' (Kunststoff)'
                name = name[:180-len(suffix)] + suffix
                counter = 2
                while Material.objects.filter(area=targets['spezial'], name=name).exclude(pk=material.pk).exists():
                    extra = f' {counter}'
                    name = material.name[:180-len(suffix)-len(extra)] + suffix + extra
                    counter += 1
            Material.objects.filter(pk=material.pk).update(area=targets['spezial'], name=name)
        # The obsolete category has no materials and can safely be removed.
        if not Material.objects.filter(area_id=source.pk).exists():
            Area.objects.filter(pk=source.pk).delete()
    # Leave any unknown/custom areas untouched rather than destroying user data.

def backwards(apps, schema_editor):
    # Reversing category consolidation automatically would misassign materials.
    # Preserve the consolidated data on migration rollback.
    pass

class Migration(migrations.Migration):
    dependencies = [('messen', '0024_sync_field_metadata_state_only')]
    operations = [migrations.RunPython(forwards, backwards)]
