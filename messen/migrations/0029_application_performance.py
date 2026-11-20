from django.db import migrations, models
import django.db.models.deletion

def seed_initial_rows(apps, schema_editor):
    # Initial values transcribed from the supplied HAMMEL brochure.
    Model = apps.get_model("messen", "ApplicationPerformance")
    tables = [[['Altholz', '12 t/h', '30 t/h', '60 t/h', '120 t/h', '230 t/h', '300 t/h'], ['Paletten', '10 t/h', '25 t/h', '50 t/h', '90 t/h', '200 t/h', '250 t/h'], ['Kabeltrommeln', '6 t/h', '20 t/h', '40 t/h', '60 t/h', '130 t/h', '160 t/h'], ['Bahnschwellen', '–', '15 t/h', '25 t/h', '50 t/h', '70 t/h', '100 t/h'], ['Wurzelstöcke', '8 t/h', '20 t/h', '35 t/h', '55 t/h', '90 t/h', '130 t/h'], ['Grünschnitt', '6 t/h', '15 t/h', '30 t/h', '50 t/h', '80 t/h', '120 t/h']], [['Hausmüll', '10 t/h', '20 t/h', '50 t/h', '100 t/h', '200 t/h', '250 t/h'], ['Industriemüll', '8 t/h', '15 t/h', '45 t/h', '80 t/h', '150 t/h', '200 t/h'], ['Sperrmüll', '8 t/h', '15 t/h', '30 t/h', '60 t/h', '110 t/h', '160 t/h'], ['Baumischabfälle', '8 t/h', '15 t/h', '35 t/h', '80 t/h', '150 t/h', '200 t/h'], ['Papier', '5 t/h', '10 t/h', '20 t/h', '45 t/h', '70 t/h', '120 t/h'], ['Papierrollen', '5 t/h', '8 t/h', '15 t/h', '30 t/h', '60 t/h', '100 t/h'], ['Altreifen', '5 t/h', '8 t/h', '20 t/h', '30 t/h', '50 t/h', '80 t/h']], [['Aluminium', '5 t/h', '8 t/h', '12 t/h', '20 t/h', '40 t/h', '80 t/h'], ['Leichter Mischschrott', '–', '7 t/h', '10 t/h', '18 t/h', '25 t/h', '50 t/h'], ['Autokarosserien', '–', '–', '–', '10 t/h', '25 t/h', '50 t/h'], ['Weiße Ware', '–', '7 t/h', '10 t/h', '20 t/h', '35 t/h', '70 t/h'], ['Motorblöcke', '–', '–', '5 t/h', '10 t/h', '15 t/h', '30 t/h']], [['Bau- und Abbruchabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Beton- und Ziegelbruch', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Kunststoffabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Gummiabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage']]]
    for area, rows in zip(("holz", "abfall", "metall", "spezial"), tables):
        for pos, values in enumerate(rows):
            Model.objects.get_or_create(
                area=area, material=values[0],
                defaults={
                    "position": pos,
                    "published": True,
                    **{f"value_{name}": value for name, value in zip(("450","650","750","850","950","1500"), values[1:])},
                },
            )

class Migration(migrations.Migration):
    dependencies = [("messen", "0028_usedmachine_languages_revision")]
    operations = [
        migrations.CreateModel(
            name="ApplicationPerformance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("area", models.CharField(choices=[("holz", "Altholz & Grünabfälle"), ("abfall", "Gewerbe-, Industrie- & Hausmüll"), ("metall", "Metallrecycling"), ("spezial", "Spezial Anwendung")], db_index=True, max_length=16, verbose_name="Einsatzbereich")),
                ("material", models.CharField(max_length=160, verbose_name="Material")),
                ("value_450", models.CharField(blank=True, max_length=40, verbose_name="450 (t/h)")),
                ("value_650", models.CharField(blank=True, max_length=40, verbose_name="650 (t/h)")),
                ("value_750", models.CharField(blank=True, max_length=40, verbose_name="750 (t/h)")),
                ("value_850", models.CharField(blank=True, max_length=40, verbose_name="850 (t/h)")),
                ("value_950", models.CharField(blank=True, max_length=40, verbose_name="950 (t/h)")),
                ("value_1500", models.CharField(blank=True, max_length=40, verbose_name="1500 (t/h)")),
                ("position", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
                ("published", models.BooleanField(default=True, verbose_name="Auf Website anzeigen")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name":"Leistungsdaten","verbose_name_plural":"Leistungsdaten","ordering":("area","position","pk")},
        ),
        migrations.RunPython(seed_initial_rows, migrations.RunPython.noop),
    ]
