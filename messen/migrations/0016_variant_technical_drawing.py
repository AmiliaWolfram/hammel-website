from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0015_official_machine_catalog")]
    operations = [
        migrations.AddField(model_name="machinevariant", name="technical_drawing", field=models.FileField(blank=True, upload_to="machine-variants/drawings/", verbose_name="Technische Zeichnung (PDF oder Bild)")),
        migrations.AddField(model_name="machinevariant", name="technical_drawing_url", field=models.URLField(blank=True, verbose_name="Technische Zeichnung URL")),
    ]
