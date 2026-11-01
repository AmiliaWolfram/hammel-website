from django.db import migrations, models
import django.db.models.deletion

def seed(apps, schema_editor):
    Machine = apps.get_model("messen", "MachineProduct")
    Used = apps.get_model("messen", "UsedMachine")
    shared = "Hydraulisch arbeitender Vorbrecher mit zwei langsam laufenden Werkzeugwellen"
    benefits = "Hohe Leistung\nNiedriger Energieverbrauch\nGeringe Geräuschentwicklung\nMinimale Staubentwicklung\nHohe Standzeit der Werkzeuge"
    data = [
      ("VB 450", "Holz, Altholz, Grünschnitt, Paletten, Haus- und Gewerbemüll", "VB 450 D: 145 PS, 8 t Maschine + 1 t Magnet\nVB 450 DK: 145 PS, 9 t Maschine + 1 t Magnet\nVB 450 E: 110 kW, 8 t Maschine + 1 t Magnet"),
      ("VB 650", "Holz, Grünschnitt, Bahnschwellen, Paletten, Haus- und Gewerbemüll, Papier", "VB 650 D: 280 PS, 16 t Maschine + 2 t Magnet\nVB 650 DK: 280 PS, 18 t Maschine + 2 t Magnet\nVB 650 E: 200 kW, 16 t Maschine + 2 t Magnet"),
      ("VB 750", "Altholz, Bau- und Abbruchholz, Wurzelstöcke, Grünschnitt, Paletten", "VB 750 D: 380 PS, 19 t Maschine + 2 t Magnet\nVB 750 DK: 380 PS, 22,5 t Maschine + 1 t Magnet\nVB 750 E: 2 × 132 kW, 20 t Maschine + 2 t Magnet"),
      ("VB 850", "Holz, Sperrmüll, Reifen, Aluminiumprofile, Papier", "VB 850 D: 450 PS, 27 t (auf Anfrage)\nVB 850 DK: 450 PS, 35 t Maschine + 3 t Magnet\nVB 850 E: 320 kW, 30 t Maschine + 3 t Magnet"),
      ("VB 950", "Holz, Sperrmüll, Reifen, Aluminiumprofile, Papier", "VB 950 DK: 760 PS, 44 t Maschine + 3 t Magnet\nVB 950 E: 2 × 250 kW, 38 t Maschine + 3 t Magnet"),
    ]
    for n,(name,apps_text,specs) in enumerate(data):
        Machine.objects.update_or_create(model_name=name, defaults=dict(category="vorbrecher", headline="HAMMEL Vorbrecher " + name[3:], description=shared if name != "VB 950" else "RED GIANT — Vorbrecher mit ineinandergreifenden Werkzeugwellen", applications=apps_text, technical_data=specs, advantages=benefits, position=n, published=True))
    used = [("VB 450 DK", "183", 2024, 5), ("VB 650 D", "1066", 2019, 1), ("VB 650 E", "85", 2000, None), ("VB 750 D", "1205", 2024, 8), ("VB 750 D", "1212", 2023, 10), ("VB 750 D", "479", 2006, 3), ("VB 950 DK", "123", 2011, 7)]
    for idx,(name,serial,year,month) in enumerate(used):
        if not Used.objects.filter(serial_number=serial).exists():
            Used.objects.create(title=name, serial_number=serial, build_year=year, build_month=month, position=idx, published=False, description="Technische Angaben und Verfügbarkeit bitte beim Vertrieb bestätigen.")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group,_ = Group.objects.get_or_create(name="Vertrieb")
    perms=Permission.objects.filter(content_type__app_label="messen", content_type__model__in=["machineproduct", "usedmachine", "usedmachinephoto"])
    group.permissions.add(*perms)

class Migration(migrations.Migration):
    dependencies = [("messen", "0009_usedmachine_details"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [
        migrations.CreateModel(name="MachineProduct", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("category", models.CharField(choices=[("vorbrecher","Vorbrecher"),("nachzerkleinerer","Nachzerkleinerer"),("siebtechnik","Siebtechnik"),("sortiertechnik","Sortiertechnik"),("anlagenbau","Anlagenbau")], max_length=30, verbose_name="Kategorie")),
            ("model_name", models.CharField(max_length=120, unique=True, verbose_name="Modell")),
            ("headline", models.CharField(blank=True,max_length=240,verbose_name="Kurzbeschreibung")),
            ("description", models.TextField(blank=True,verbose_name="Beschreibung")),
            ("applications", models.TextField(blank=True,verbose_name="Einsatzgebiete")),
            ("technical_data", models.TextField(blank=True,verbose_name="Technische Daten (je Zeile)")),
            ("advantages", models.TextField(blank=True,verbose_name="Vorteile (je Zeile)")),
            ("image", models.ImageField(blank=True,upload_to="machine-products/",verbose_name="Produktfoto")),
            ("image_url", models.URLField(blank=True,verbose_name="Bild-URL (optional)")),
            ("datasheet_url", models.URLField(blank=True,verbose_name="Datenblatt-URL")),
            ("published", models.BooleanField(default=True,verbose_name="Öffentlich sichtbar")),
            ("position", models.PositiveIntegerField(default=0,verbose_name="Reihenfolge")),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ],options={"ordering":["position","model_name"],"verbose_name":"Maschinenmodell","verbose_name_plural":"Maschinenkatalog"}),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
