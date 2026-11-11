from django.db import migrations, models
import django.db.models.deletion

def seed(apps, schema_editor):
    Department = apps.get_model("recruiting", "VacancyDepartment")
    names = ["Vertrieb", "Service", "Einkauf", "Konstruktion", "Verwaltung", "Produktion"]
    for i, name in enumerate(names, 1):
        Department.objects.get_or_create(name=name, defaults={"sort_order": i * 10})

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0009_hrtextblock_profession")]
    operations = [
        migrations.CreateModel(name="VacancyDepartment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=120, unique=True, verbose_name="Abteilung")),
            ("active", models.BooleanField(default=True, verbose_name="Aktiv")),
            ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
        ], options={"ordering": ("sort_order", "name"), "verbose_name": "Stellenabteilung", "verbose_name_plural": "Stellenabteilungen"}),
        migrations.AddField(model_name="vacancy", name="department", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vacancies", to="recruiting.vacancydepartment", verbose_name="Abteilung (nur Stellenangebote)")),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
