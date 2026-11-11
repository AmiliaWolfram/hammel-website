from django.core.management.base import BaseCommand
from django.db import transaction
from recruiting.models import VacancyDepartment, ApplicationDepartment, HRTextBlock, Vacancy
from pathlib import Path
import json

JOB_DEPARTMENTS = ("Vertrieb", "Service", "Einkauf", "Konstruktion", "Verwaltung", "Produktion")
APPLICATION_DEPARTMENTS = ("Produktion", "Konstruktion", "Service", "Vertrieb", "Verwaltung", "Logistik", "Ausbildung / Praktikum", "Sonstiges")
CATEGORIES = ("responsibilities", "hard_skills", "soft_skills", "benefits")
DATA_FILE = Path(__file__).with_name("hr_profession_catalog.json")

class Command(BaseCommand):
    help = "Befüllt die HR-Bibliothek mit allen Berufsprofilen; bestehende Daten bleiben erhalten."

    @transaction.atomic
    def handle(self, *args, **options):
        counts = {"Abteilungen": 0, "Bewerbungsbereiche": 0, "Textbausteine": 0}
        for i, name in enumerate(JOB_DEPARTMENTS, 1):
            _, created = VacancyDepartment.objects.get_or_create(name=name, defaults={"active": True, "sort_order": i * 10})
            counts["Abteilungen"] += int(created)
        for i, name in enumerate(APPLICATION_DEPARTMENTS, 1):
            _, created = ApplicationDepartment.objects.get_or_create(name=name, defaults={"active": True, "sort_order": i * 10})
            counts["Bewerbungsbereiche"] += int(created)
        profiles = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        # The existing schema stores one profession per unique text block. A text
        # shared by several profiles stays general (profession="") so it remains
        # available for every profile; profile-specific items keep their key.
        occurrences = {}
        for key, profile in profiles.items():
            if key == "other":
                continue
            for category in CATEGORIES:
                for text in profile.get(category, []):
                    text = text.strip()
                    if text and len(text) <= 300:
                        occurrences.setdefault((category, text), set()).add(key)
        for (category, text), keys in occurrences.items():
            profession = next(iter(keys)) if len(keys) == 1 else ""
            _, created = HRTextBlock.objects.get_or_create(
                category=category, text=text,
                defaults={"active": True, "profession": profession})
            counts["Textbausteine"] += int(created)
        for label, count in counts.items():
            self.stdout.write(f"{label}: {count} neue Einträge")
        self.stdout.write(self.style.SUCCESS(
            f"Fertig: {len(profiles)} Berufsprofile im Stellenbaukasten. Bestehende Stellen und Bewerbungen unverändert."))
        self.stdout.write("Hinweis: Vorteile sind redaktionelle Vorschläge und vor Veröffentlichung durch HR zu prüfen.")
