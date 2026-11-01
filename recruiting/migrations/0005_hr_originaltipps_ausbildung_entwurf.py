from django.db import migrations


def apply_hr_content(apps, schema_editor):
    HRTip = apps.get_model("recruiting", "HRTip")
    Vacancy = apps.get_model("recruiting", "Vacancy")

    # Alte Demonstrations-Tipps nur entfernen, wenn sie noch unverändert sind.
    old_titles = [
        "DEIN LEBENSLAUF", "ZEUGNISSE UND ZERTIFIKATE",
        "ZEIG UNS DEINE MOTIVATION", "DAS PERSÖNLICHE GESPRÄCH",
    ]
    for title in old_titles:
        HRTip.objects.filter(title=title).delete()

    tips = [
        ("BEWERBUNGSUNTERLAGEN", "Achte darauf, dass deine Bewerbungsunterlagen vollständig sind. Gestalte deinen Lebenslauf übersichtlich und halte ihn aktuell. Ein Bewerbungsfoto kannst du gerne beifügen, es ist aber kein Muss."),
        ("VORSTELLUNGSGESPRÄCH", "Informiere dich vor dem Gespräch über HAMMEL und unser Unternehmen. Überlege dir, warum du Teil unseres Teams werden möchtest."),
        ("AUTHENTIZITÄT", "Bleib einfach du selbst. Sprich offen über deine Stärken, bisherigen Erfahrungen und Interessen."),
        ("VORBEREITUNG", "Bring gerne eigene Fragen mit. Nutze das Gespräch auch als Gelegenheit, HAMMEL und die Menschen hinter dem Unternehmen besser kennenzulernen."),
        ("BEWERBUNGSPROZESS", "Bewirb dich möglichst frühzeitig. Wenn du noch Fragen hast, kannst du jederzeit Kontakt mit uns aufnehmen."),
    ]
    for order, (title, body) in enumerate(tips, start=1):
        obj, created = HRTip.objects.get_or_create(
            title=title, defaults={"body": body, "order": order * 10, "published": True}
        )

    # Von HR genannte Ausbildungsberufe als ENTWÜRFE: erst nach Freigabe veröffentlichen.
    for order, title in enumerate([
        "Ausbildung Kaufmann/-frau für Groß- und Außenhandelsmanagement",
        "Ausbildung Industriekaufmann/-frau",
        "Ausbildung Konstruktionsmechaniker/-in",
    ], start=1):
        # Datenmigrationen verwenden historische Modelle: deren save()-Methode
        # generiert KEINEN Slug. Deshalb hier explizit setzen.
        from django.utils.text import slugify
        existing = Vacancy.objects.filter(title=title).first()
        if existing:
            continue
        base = slugify(title)[:190] or "ausbildung"
        # Existierende Slugs nie überschreiben; neue Stellen erhalten einen
        # eindeutigen Slug, auch wenn ähnliche Titel bereits vorhanden sind.
        slug = base
        suffix = 2
        while Vacancy.objects.filter(slug=slug).exists():
            slug = f"{base}-{suffix}"
            suffix += 1
        Vacancy.objects.create(
            title=title, slug=slug,
            category="ausbildung", published=False,
            sort_order=order * 10,
            introduction="Entwurf – Stellenanzeige wird intern abgestimmt. Nicht veröffentlichen, bevor der freigegebene Text vorliegt.",
        )


class Migration(migrations.Migration):
    dependencies = [("recruiting", "0004_seed_hr_tips")]
    operations = [migrations.RunPython(apply_hr_content, migrations.RunPython.noop)]
