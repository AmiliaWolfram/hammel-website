from django.db import migrations
from django.utils.text import slugify

SOURCE_URL = "https://www.hammel.de/index.php/de/karriere"
INTRO = 'Werde Teil des HAMMEL-Teams und gestalte mit uns die Zukunft der Recyclingtechnik.'
DATA = [('Servicetechniker', 'Service', 'Wartung und Reparatur von Großmaschinen\nKunden bei Fragen und technischen Problemen unterstützen\nStörungen erkennen und zuverlässig beheben', 'Technisches Verständnis und praktische Arbeitsweise', 'Selbstständigkeit und hohe Einsatzbereitschaft\nBereitschaft zu Montageeinsätzen\nKundenorientierung', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKostenloses warmes Mittagessen\nKollegiales Team'), ('Metallbauer / Schlosser', 'Produktion', 'Technische Zeichnungen in Werkstücke umsetzen\nStahl und Bleche mit geeigneten Werkzeugen bearbeiten\nBaugruppen zusammenfügen\nBauteile sorgfältig vermessen', 'Technische Pläne und Zeichnungen lesen\nPräzises Arbeiten mit Metall', 'Teamfähigkeit\nSicherer Umgang mit einem dynamischen Werkstattumfeld', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKaffee\nKollegiales Team\nKostenloses warmes Mittagessen'), ('Kaufmännischer Mitarbeiter', 'Verwaltung', 'Tägliche Prozesse effizient gestalten und optimieren\nRelevante Daten filtern, bündeln und bereitstellen\nDokumente strukturiert ablegen', 'Kaufmännische Ausbildung oder ausgeprägtes Organisationstalent\nSchnelle Auffassungsgabe', 'Teamfähigkeit und Engagement\nAuch in turbulenten Situationen den Überblick behalten\nEigeninitiative', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKaffee\nKollegiales Team\nKostenloses warmes Mittagessen'), ('Deal-Maker / Vertriebsheld im Innendienst', 'Vertrieb', 'Kundenanfragen und Kommunikation koordinieren\nAngebote, Aufträge und Abläufe betreuen\nKunden lösungsorientiert begleiten\nMit Außendienst, Logistik und Buchhaltung zusammenarbeiten', 'Kaufmännische Ausbildung oder Vertriebserfahrung\nKenntnisse in MS Office', 'Kommunikationsfreude und Kundenorientierung\nOrganisationstalent\nBelastbarkeit bei vielen Anfragen', 'Kostenloses Mittagessen\nKaffee'), ('Mediengestalter', 'Vertrieb', 'Beiträge für Social Media, Website und Printmedien gestalten\nIdeen für die Unternehmenskommunikation entwickeln\nFotos und Grafiken bearbeiten', 'Sicherer Umgang mit Design- und Bildbearbeitungsprogrammen\nAussagekräftige Arbeitsproben', 'Selbstständige und strukturierte Arbeitsweise\nKreativität', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKaffee\nKollegiales Team\nKostenloses warmes Mittagessen'), ('Recruiter / Personalreferent', 'Verwaltung', 'Recruiting von der Suche bis zur Vertragsunterschrift begleiten\nBewerbungsprozesse gestalten\nMit Fachbereichen zusammenarbeiten\nEmployer Branding weiterentwickeln\nStellenanzeigen erstellen', 'Erfahrung im Recruiting oder Active Sourcing (z. B. LinkedIn, Xing) oder großes Interesse am HR-Bereich\nFließende Deutschkenntnisse', 'Eigeninitiative\nKommunikationsstärke\nOrganisationsfähigkeit und Entscheidungsfreude', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKaffee\nKollegiales Team\nKostenloses warmes Mittagessen'), ('Lagerist', 'Einkauf', 'Lieferungen annehmen und Qualität prüfen\nBestände verwalten\nMontage und Fertigung mit Bauteilen versorgen\nGüter mit dem Gabelstapler transportieren', 'Gültiger Gabelstaplerschein\nIdealerweise Erfahrung in Lager, Logistik oder Versand\nGute Deutschkenntnisse', 'Zuverlässigkeit und Teamfähigkeit\nKörperliche Belastbarkeit', 'Geregelte Arbeitszeiten ohne Schichtdienst\nKostenfreier Mitarbeiterparkplatz\nKollegiales Team\nKostenloses warmes Mittagessen')]
AUSBILDUNG_BENEFITS = 'Ausbildungsvergütung\nKostenfreie Betriebskantine\nPraxisnahe Ausbildung im Unternehmen\nMonatlich 50 € Tankgutschein\nAnteilige Übernahme von Übernachtungskosten an der Berufsschule'
AUSBILDUNG_REQ = '(Bald) Schulabschluss\nInteresse an Theorie und Praxis\nMotivation für abwechslungsreiche Aufgaben und Teamarbeit'

def seed_original_positions(apps, schema_editor):
    Vacancy = apps.get_model("recruiting", "Vacancy")
    Department = apps.get_model("recruiting", "VacancyDepartment")
    for index, (title, dept, tasks, hard, soft, benefits) in enumerate(DATA, 1):
        if Vacancy.objects.filter(title__iexact=title, category="job").exists():
            continue
        department = Department.objects.filter(name=dept).first()
        base = slugify(title)[:180] or "stelle"
        slug = base
        i = 2
        while Vacancy.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"; i += 1
        Vacancy.objects.create(title=title, slug=slug, category="job", department=department,
            location="Bad Salzungen", employment_type="Stellenangebot", introduction=INTRO,
            responsibilities=tasks, hard_skills=hard, soft_skills=soft,
            benefits=benefits, published=False, sort_order=index * 10)
    # The old site also lists Fachkraft für Lagerlogistik as an apprenticeship.
    title = "Ausbildung Fachkraft für Lagerlogistik"
    if not Vacancy.objects.filter(title__iexact=title, category="ausbildung").exists():
        base = slugify(title)[:180]
        slug = base
        i = 2
        while Vacancy.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"; i += 1
        Vacancy.objects.create(title=title, slug=slug, category="ausbildung",
            location="Bad Salzungen", employment_type="Ausbildung", published=False,
            introduction="Ausbildungsberuf auf der bisherigen HAMMEL-Karriereseite gelistet. Eine berufsspezifische Aufgabenbeschreibung ist dort nicht angegeben.",
            requirements=AUSBILDUNG_REQ, benefits=AUSBILDUNG_BENEFITS, sort_order=40)
    # Preserve any edited descriptions; fill empty benefits/requirements of existing training vacancies only.
    for vacancy in Vacancy.objects.filter(category="ausbildung"):
        updates = {}
        if not vacancy.benefits: updates["benefits"] = AUSBILDUNG_BENEFITS
        if not vacancy.requirements and not vacancy.hard_skills and not vacancy.soft_skills:
            updates["requirements"] = AUSBILDUNG_REQ
        if updates: Vacancy.objects.filter(pk=vacancy.pk).update(**updates)

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0011_hammel_department_names")]
    operations = [migrations.RunPython(seed_original_positions, migrations.RunPython.noop)]
