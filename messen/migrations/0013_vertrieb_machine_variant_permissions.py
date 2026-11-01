from django.db import migrations

def grant_variant_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group, _ = Group.objects.get_or_create(name="Vertrieb")
    group.permissions.add(*Permission.objects.filter(content_type__app_label="messen", content_type__model__in=["machineproduct", "machinevariant"]))

class Migration(migrations.Migration):
    dependencies = [("messen", "0012_variant_hero_video")]
    operations = [migrations.RunPython(grant_variant_permissions, migrations.RunPython.noop)]
