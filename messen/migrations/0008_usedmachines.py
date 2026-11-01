from django.db import migrations, models
import django.db.models.deletion

def seed(apps, schema_editor):
    Machine = apps.get_model("messen", "UsedMachine")
    records = [("VB 450 DK #183", "183", 2024, 5), ("VB 650 D #1066", "1066", 2019, 1), ("VB 650 E #85", "85", 2000, None), ("VB 750 D #1205", "1205", 2024, 8), ("VB 750 D #1212", "1212", 2023, 10), ("VB 750 D #479", "479", 2006, 3), ("VB 950 DK #123", "123", 2011, 7)]
    for i,(title,serial,year,month) in enumerate(records):
        Machine.objects.get_or_create(serial_number=serial, defaults={"title":title,"build_year":year,"build_month":month,"position":i,"published":False})

class Migration(migrations.Migration):
    dependencies = [("messen", "0007_internal_news_links")]
    operations = [
        migrations.CreateModel(name="UsedMachine", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("title", models.CharField(max_length=180, verbose_name="Maschinenbezeichnung")),
            ("serial_number", models.CharField(blank=True, max_length=70, verbose_name="Maschinennummer")),
            ("build_year", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Baujahr")),
            ("build_month", models.PositiveSmallIntegerField(blank=True, null=True, choices=[(i,str(i)) for i in range(1,13)], verbose_name="Baumonat")),
            ("operating_hours", models.CharField(blank=True, max_length=90, verbose_name="Betriebsstunden")),
            ("engine", models.CharField(blank=True, max_length=220, verbose_name="Motor")),
            ("power", models.CharField(blank=True, max_length=100, verbose_name="Leistung")),
            ("shafts", models.TextField(blank=True, verbose_name="Wellen / Werkzeuge")),
            ("equipment", models.TextField(blank=True, verbose_name="Ausstattung")),
            ("weight", models.CharField(blank=True, max_length=100, verbose_name="Gewicht")),
            ("description", models.TextField(blank=True, verbose_name="Beschreibung")),
            ("image", models.ImageField(blank=True, upload_to="used-machines/", verbose_name="Hauptbild")),
            ("video_url", models.URLField(blank=True, verbose_name="YouTube Video")),
            ("published", models.BooleanField(default=False, verbose_name="Auf Website sichtbar")),
            ("position", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ["position", "-id"], "verbose_name": "Gebrauchtmaschine", "verbose_name_plural": "Gebrauchtmaschinen"}),
        migrations.CreateModel(name="UsedMachinePhoto", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("image", models.ImageField(upload_to="used-machines/gallery/", verbose_name="Foto")),
            ("caption", models.CharField(blank=True, max_length=180, verbose_name="Bildunterschrift")),
            ("position", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
            ("machine", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="messen.usedmachine")),
        ], options={"ordering": ["position", "id"]}),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]

