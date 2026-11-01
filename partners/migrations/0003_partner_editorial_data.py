import json
from pathlib import Path
from django.db import migrations, models


def populate(apps, schema_editor):
    Partner = apps.get_model("partners", "Partner")
    data = json.loads((Path(__file__).resolve().parent.parent / "legacy_partner_content.json").read_text(encoding="utf-8"))
    by_domain = data["domains"]
    logos = data["logos_by_name"]
    for p in Partner.objects.all().iterator():
        content = by_domain.get(p.domain, {})
        updates = {}
        mapping = {'eyebrow': 'eyebrow', 'description': 'description', 'specialties': 'specialties', 'source': 'source_url', 'theme': 'theme', 'tagline': 'tagline', 'brandColor': 'brand_color', 'heroImage': 'hero_image', 'officialLogo': 'official_logo'}
        for source, target in mapping.items():
            value = content.get(source)
            if value and not getattr(p, target):
                updates[target] = value
        if not p.logo and not p.logo_url and logos.get(p.name):
            updates["logo_url"] = logos[p.name]
        if updates:
            Partner.objects.filter(pk=p.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [("partners", "0002_seed")]
    operations = [
        migrations.AddField(model_name="partner",name="eyebrow",field=models.CharField(max_length=300,blank=True)),
        migrations.AddField(model_name="partner",name="specialties",field=models.JSONField(default=list,blank=True)),
        migrations.AddField(model_name="partner",name="source_url",field=models.URLField(max_length=600,blank=True)),
        migrations.AddField(model_name="partner",name="theme",field=models.CharField(max_length=40,blank=True)),
        migrations.AddField(model_name="partner",name="tagline",field=models.CharField(max_length=250,blank=True)),
        migrations.AddField(model_name="partner",name="brand_color",field=models.CharField(max_length=7,blank=True)),
        migrations.AddField(model_name="partner",name="hero_image",field=models.URLField(max_length=700,blank=True)),
        migrations.AddField(model_name="partner",name="official_logo",field=models.URLField(max_length=700,blank=True)),
        migrations.RunPython(populate, migrations.RunPython.noop),
    ]
