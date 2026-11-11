from django.db import migrations

DEPARTMENTS = ("Vertrieb", "Service", "Einkauf", "Konstruktion", "Verwaltung", "Produktion")
OLD_NAMES = {
    "Vertrieb & Marketing": "Vertrieb",
    "Service & Technik": "Service",
    "Verwaltung & Einkauf": "Verwaltung",
    "Produktion & Fertigung": "Produktion",
}

def update_departments(apps, schema_editor):
    Department = apps.get_model("recruiting", "VacancyDepartment")
    Vacancy = apps.get_model("recruiting", "Vacancy")
    # Retain assignments for renamed departments, including existing target names.
    for old_name, new_name in OLD_NAMES.items():
        old = Department.objects.filter(name=old_name).first()
        if not old:
            continue
        target = Department.objects.filter(name=new_name).first()
        if target:
            Vacancy.objects.filter(department_id=old.pk).update(department_id=target.pk)
            old.delete()
        else:
            old.name = new_name
            old.save(update_fields=["name"])
    # Unknown historical groups must not be silently assigned to an incorrect department.
    # Their vacancies remain intact, but require explicit reclassification.
    Department.objects.exclude(name__in=DEPARTMENTS).update(active=False)
    for position, name in enumerate(DEPARTMENTS, start=1):
        department, _ = Department.objects.get_or_create(name=name)
        department.sort_order = position * 10
        department.active = True
        department.save(update_fields=["sort_order", "active"])

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0010_vacancy_departments")]
    operations = [migrations.RunPython(update_departments, noop)]
