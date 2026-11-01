from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0011_machine_variants")]
    operations = [
        migrations.AddField(model_name="machinevariant", name="hero_video", field=models.FileField(blank=True, upload_to="machine-variants/videos/", verbose_name="Hero-Video (MP4/WebM)")),
        migrations.AddField(model_name="machinevariant", name="hero_video_url", field=models.URLField(blank=True, verbose_name="Hero-Video URL (MP4/WebM)")),
    ]
