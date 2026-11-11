from django.db import migrations

OLD_INTRO = 'Bei HAMMEL zählt, dass du ins Team passt. Die folgenden Angaben wurden von der bisherigen HAMMEL-Karriereseite übernommen und für den neuen Stelleneditor strukturiert.'
NEW_INTRO = "Werde Teil des HAMMEL-Teams und gestalte mit uns die Zukunft der Recyclingtechnik."

def clean_imported_intros(apps, schema_editor):
    Vacancy = apps.get_model("recruiting", "Vacancy")
    Vacancy.objects.filter(introduction=OLD_INTRO).update(introduction=NEW_INTRO)

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0012_seed_original_hammel_positions")]
    operations = [migrations.RunPython(clean_imported_intros, migrations.RunPython.noop)]
