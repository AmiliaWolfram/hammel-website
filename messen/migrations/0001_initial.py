from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Messe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, verbose_name="Messename")),
                ("start_date", models.DateField(verbose_name="Beginn")),
                ("end_date", models.DateField(verbose_name="Ende")),
                ("city", models.CharField(max_length=100, verbose_name="Stadt")),
                ("country", models.CharField(blank=True, max_length=100, verbose_name="Land")),
                ("booth", models.CharField(blank=True, max_length=100, verbose_name="Halle / Stand")),
                ("description", models.TextField(blank=True, verbose_name="Beschreibung")),
                ("url", models.URLField(blank=True, verbose_name="Messe-Website")),
                ("published", models.BooleanField(default=False, verbose_name="Öffentlich sichtbar")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["start_date", "title"], "verbose_name": "Messe", "verbose_name_plural": "Messen"},
        )
    ]
