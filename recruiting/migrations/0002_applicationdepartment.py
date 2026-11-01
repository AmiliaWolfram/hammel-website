from django.db import migrations, models


def seed_departments(apps, schema_editor):
    Department = apps.get_model("recruiting", "ApplicationDepartment")
    for position, name in enumerate(("Produktion", "Konstruktion", "Service", "Vertrieb", "Verwaltung", "Logistik", "Ausbildung / Praktikum", "Sonstiges"), 1):
        Department.objects.get_or_create(name=name, defaults={"sort_order": position})


class Migration(migrations.Migration):
    dependencies = [("recruiting", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ApplicationDepartment",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Bereich")),
                ("active", models.BooleanField(default=True, verbose_name="In der Bewerbung anzeigen")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")),
            ],
            options={"verbose_name": "Bewerbungsbereich", "verbose_name_plural": "Bewerbungsbereiche", "ordering": ["sort_order", "name"]},
        ),
        migrations.RunPython(seed_departments, migrations.RunPython.noop),
    ]
