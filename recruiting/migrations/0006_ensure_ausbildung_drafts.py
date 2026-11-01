from django.db import migrations
from django.utils.text import slugify

TITLES = (
    "Ausbildung Kaufmann/-frau für Groß- und Außenhandelsmanagement",
    "Ausbildung Industriekaufmann/-frau",
    "Ausbildung Konstruktionsmechaniker/-in",
)

def seed_draft_vacancies(apps, schema_editor):
    Vacancy = apps.get_model("recruiting", "Vacancy")
    for index, title in enumerate(TITLES, 1):
        if Vacancy.objects.filter(title=title).exists():
            continue
        base = slugify(title)[:180] or "ausbildung"
        slug = base
        n = 2
        while Vacancy.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        Vacancy.objects.create(
            title=title, slug=slug, category="ausbildung",
            location="Bad Salzungen", published=False,
            sort_order=index * 10,
            introduction="Stellenanzeige wird derzeit intern abgestimmt.",
        )

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0005_hr_originaltipps_ausbildung_entwurf")]
    operations = [migrations.RunPython(seed_draft_vacancies, migrations.RunPython.noop)]
