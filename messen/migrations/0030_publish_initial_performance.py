from django.db import migrations

def publish_existing_seed_rows(apps, schema_editor):
    """Publish only unchanged initial brochure values; do not overwrite staff edits."""
    Model = apps.get_model("messen", "ApplicationPerformance")
    tables = [[['Altholz', '12 t/h', '30 t/h', '60 t/h', '120 t/h', '230 t/h', '300 t/h'], ['Paletten', '10 t/h', '25 t/h', '50 t/h', '90 t/h', '200 t/h', '250 t/h'], ['Kabeltrommeln', '6 t/h', '20 t/h', '40 t/h', '60 t/h', '130 t/h', '160 t/h'], ['Bahnschwellen', '–', '15 t/h', '25 t/h', '50 t/h', '70 t/h', '100 t/h'], ['Wurzelstöcke', '8 t/h', '20 t/h', '35 t/h', '55 t/h', '90 t/h', '130 t/h'], ['Grünschnitt', '6 t/h', '15 t/h', '30 t/h', '50 t/h', '80 t/h', '120 t/h']], [['Hausmüll', '10 t/h', '20 t/h', '50 t/h', '100 t/h', '200 t/h', '250 t/h'], ['Industriemüll', '8 t/h', '15 t/h', '45 t/h', '80 t/h', '150 t/h', '200 t/h'], ['Sperrmüll', '8 t/h', '15 t/h', '30 t/h', '60 t/h', '110 t/h', '160 t/h'], ['Baumischabfälle', '8 t/h', '15 t/h', '35 t/h', '80 t/h', '150 t/h', '200 t/h'], ['Papier', '5 t/h', '10 t/h', '20 t/h', '45 t/h', '70 t/h', '120 t/h'], ['Papierrollen', '5 t/h', '8 t/h', '15 t/h', '30 t/h', '60 t/h', '100 t/h'], ['Altreifen', '5 t/h', '8 t/h', '20 t/h', '30 t/h', '50 t/h', '80 t/h']], [['Aluminium', '5 t/h', '8 t/h', '12 t/h', '20 t/h', '40 t/h', '80 t/h'], ['Leichter Mischschrott', '–', '7 t/h', '10 t/h', '18 t/h', '25 t/h', '50 t/h'], ['Autokarosserien', '–', '–', '–', '10 t/h', '25 t/h', '50 t/h'], ['Weiße Ware', '–', '7 t/h', '10 t/h', '20 t/h', '35 t/h', '70 t/h'], ['Motorblöcke', '–', '–', '5 t/h', '10 t/h', '15 t/h', '30 t/h']], [['Bau- und Abbruchabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Beton- und Ziegelbruch', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Kunststoffabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage'], ['Gummiabfälle', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage', 'auf Anfrage']]]
    for area, rows in zip(("holz", "abfall", "metall", "spezial"), tables):
        for values in rows:
            expected = {f"value_{name}": value for name, value in zip(
                ("450", "650", "750", "850", "950", "1500"), values[1:]
            )}
            Model.objects.filter(
                area=area, material=values[0], published=False, **expected
            ).update(published=True)

class Migration(migrations.Migration):
    dependencies = [("messen", "0029_application_performance")]
    operations = [migrations.RunPython(publish_existing_seed_rows, migrations.RunPython.noop)]
