from django.db import migrations


def seed_tips(apps, schema_editor):
    HRTip = apps.get_model("recruiting", "HRTip")
    examples = [
        ("DEIN LEBENSLAUF", "Ein übersichtlicher Lebenslauf hilft uns, deine Erfahrungen schnell kennenzulernen. Gib deine bisherigen Tätigkeiten, Ausbildungen und relevanten Kenntnisse an. Achte darauf, dass deine Kontaktdaten aktuell sind.\n\nTipp: Beschreibe praktische Aufgaben möglichst konkret, zum Beispiel welche Maschinen, Werkzeuge oder Programme du bereits eingesetzt hast."),
        ("ZEUGNISSE UND ZERTIFIKATE", "Füge die Nachweise bei, die für deine gewünschte Tätigkeit wichtig sind, etwa Ausbildungs- oder Arbeitszeugnisse und passende Zertifikate. Du kannst mehrere Dokumente in der Bewerbung hochladen.\n\nTipp: Benenne die Dateien verständlich und prüfe vor dem Absenden, ob sie sich öffnen lassen."),
        ("ZEIG UNS DEINE MOTIVATION", "Wir möchten wissen, welcher Bereich dich interessiert und was du bei HAMMEL einbringen möchtest. Ein kurzer persönlicher Text ist hilfreicher als eine allgemeine Standardbewerbung.\n\nTipp: Nenne eine Aufgabe oder Erfahrung, die besonders gut zur gewünschten Tätigkeit passt."),
        ("DAS PERSÖNLICHE GESPRÄCH", "Wenn wir dich zu einem Gespräch einladen, möchten wir dich und deine Erwartungen besser kennenlernen. Informiere dich vorab über HAMMEL und überlege, welche Fragen du zu den Aufgaben und zum Team hast.\n\nTipp: Du musst nicht auf jede Frage sofort eine perfekte Antwort haben. Konkrete Beispiele aus deiner Praxis sind oft am hilfreichsten."),
    ]
    for position, (title, body) in enumerate(examples, start=1):
        if not HRTip.objects.filter(title=title).exists():
            HRTip.objects.create(title=title, body=body, order=position * 10, published=True)


class Migration(migrations.Migration):
    dependencies = [("recruiting", "0003_applicationcertificate")]
    operations = [migrations.RunPython(seed_tips, migrations.RunPython.noop)]
