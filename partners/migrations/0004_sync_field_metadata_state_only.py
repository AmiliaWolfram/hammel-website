"""Synchronize historical Django field metadata without database schema changes."""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('partners', '0003_partner_editorial_data')]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
            migrations.AlterField(model_name='partner', name='brand_color', field=models.CharField("Akzentfarbe", max_length=7, blank=True)),
            migrations.AlterField(model_name='partner', name='eyebrow', field=models.CharField("Kurzzeile", max_length=300, blank=True)),
            migrations.AlterField(model_name='partner', name='hero_image', field=models.URLField("Titelbild-URL", max_length=700, blank=True)),
            migrations.AlterField(model_name='partner', name='official_logo', field=models.URLField("Offizielles Markenlogo", max_length=700, blank=True)),
            migrations.AlterField(model_name='partner', name='source_url', field=models.URLField("Quelle", max_length=600, blank=True)),
            migrations.AlterField(model_name='partner', name='specialties', field=models.JSONField("Schwerpunkte", default=list, blank=True)),
            migrations.AlterField(model_name='partner', name='tagline', field=models.CharField("Markenclaim", max_length=250, blank=True)),
            migrations.AlterField(model_name='partner', name='theme', field=models.CharField("Designvariante", max_length=40, blank=True))
            ],
        ),
    ]
