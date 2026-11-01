from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0018_editor_workflow")]
    operations = [migrations.AddField(model_name="machinevariant", name="hero_media_choice", field=models.CharField(choices=[("auto", "Automatisch"), ("video", "Video"), ("image", "Foto")], default="auto", max_length=10, verbose_name="Hero-Darstellung"))]
