from django.db import migrations

DATA = [
('Ausbildung Kaufmann/-frau für Groß- und Außenhandelsmanagement', 'Lerne, wie Maschinen und Ersatzteile international angeboten, verkauft und organisiert werden. Du erhältst Einblicke in Einkauf, Vertrieb und die Zusammenarbeit mit unseren Kunden und Partnern.', 'Anfragen bearbeiten und Angebote vorbereiten\nBestellungen und Liefertermine koordinieren\nKunden und internationale Geschäftspartner betreuen\nAbläufe im Einkauf und Vertrieb kennenlernen', 'Interesse an kaufmännischen Abläufen und internationalen Märkten\nSorgfältige und zuverlässige Arbeitsweise\nFreude an Kommunikation und Teamarbeit', 'Einblicke in unterschiedliche kaufmännische Bereiche\nPraxisnahes Lernen in einem international tätigen Industrieunternehmen\nZusammenarbeit mit erfahrenen Kolleginnen und Kollegen'),
('Ausbildung Industriekaufmann/-frau', 'Entdecke die kaufmännischen Prozesse hinter unserer Recyclingtechnik. Während deiner Ausbildung lernst du, wie verschiedene Abteilungen zusammenarbeiten und ein Industrieunternehmen organisiert wird.', 'Kaufmännische Abläufe in Einkauf und Verwaltung unterstützen\nAufträge und Dokumente bearbeiten\nPlanung und Organisation im Tagesgeschäft kennenlernen\nMit unterschiedlichen Fachabteilungen zusammenarbeiten', 'Interesse an Wirtschaft und Organisation\nStrukturierte Arbeitsweise und Lernbereitschaft\nTeamfähigkeit und Freude am Umgang mit Menschen', 'Abwechslungsreiche Einblicke in betriebliche Abläufe\nPraxisnahe Aufgaben und persönliche Ansprechpartner\nErfahrung in einem produzierenden Unternehmen'),
('Ausbildung Konstruktionsmechaniker/-in', 'Arbeite dort, wo aus Metall leistungsstarke Recyclingmaschinen entstehen. In dieser Ausbildung lernst du die Bearbeitung und Montage von Bauteilen sowie den Umgang mit technischen Zeichnungen kennen.', 'Metallbauteile fertigen und bearbeiten\nTechnische Zeichnungen lesen und umsetzen\nBauteile und Baugruppen montieren\nWerkzeuge, Maschinen und Fertigungsverfahren kennenlernen', 'Interesse an Technik und handwerklicher Arbeit\nRäumliches Vorstellungsvermögen und Genauigkeit\nMotivation, Neues zu lernen und im Team zu arbeiten', 'Praktische Einblicke in die Fertigung von Recyclingmaschinen\nArbeit mit technischen Zeichnungen und Metallbauteilen\nBegleitung durch erfahrene Fachkräfte'),
]

def update_examples(apps, schema_editor):
    Vacancy = apps.get_model('recruiting', 'Vacancy')
    for title, intro, tasks, reqs, benefits in DATA:
        Vacancy.objects.filter(title=title, category='ausbildung').update(
            introduction=intro, responsibilities=tasks, requirements=reqs,
            benefits=benefits, employment_type='Ausbildung', published=False,
        )

class Migration(migrations.Migration):
    dependencies = [('recruiting', '0006_ensure_ausbildung_drafts')]
    operations = [migrations.RunPython(update_examples, migrations.RunPython.noop)]
