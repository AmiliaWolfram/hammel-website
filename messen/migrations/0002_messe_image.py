from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0001_initial")]
    operations = [migrations.AddField(
        model_name="messe", name="image",
        field=models.ImageField(blank=True, upload_to="messen/", verbose_name="Messebild"),
    )]
