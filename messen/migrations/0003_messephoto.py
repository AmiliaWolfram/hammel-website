from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("messen", "0002_messe_image")]
    operations = [migrations.CreateModel(name="MessePhoto", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("image", models.ImageField(upload_to="messen/gallery/", verbose_name="Galeriefoto")),
        ("caption", models.CharField(blank=True, max_length=180, verbose_name="Bildunterschrift")),
        ("position", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
        ("messe", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="messen.messe", verbose_name="Messe")),
    ], options={"ordering": ["position", "id"], "verbose_name": "Messefoto", "verbose_name_plural": "Messefotos"})]
