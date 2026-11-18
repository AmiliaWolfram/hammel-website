from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0026_remove_machinevariant_datasheet_url")]
    operations = [migrations.AddField(model_name="machinevariant", name="visible_languages", field=models.JSONField(blank=True, default=None, null=True, verbose_name="Aktivierte Sprachversionen"))]
