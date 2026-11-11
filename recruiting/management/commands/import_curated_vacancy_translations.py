"""Import reviewed draft translations without overwriting any existing data."""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from recruiting.models import Vacancy
from translations.models import ContentTranslation
from translations.services import fingerprint

class Command(BaseCommand):
    help = "Add curated missing vacancy translations; never overwrite existing records."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        source = Path(__file__).resolve().parents[3] / "data" / "curated_vacancy_translations.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        ct = ContentType.objects.get_for_model(Vacancy)
        count = 0
        skipped = 0
        with transaction.atomic():
            for german_title, versions in payload.items():
                matches = list(Vacancy.objects.filter(title=german_title))
                if len(matches) != 1:
                    self.stdout.write(self.style.WARNING(f"Skipped ambiguous/missing vacancy: {german_title}"))
                    continue
                vacancy = matches[0]
                for language, fields in versions.items():
                    for field, text in fields.items():
                        original = getattr(vacancy, field, "") or ""
                        if not original.strip() or not text.strip():
                            continue
                        if ContentTranslation.objects.filter(content_type=ct, object_id=vacancy.pk, field_name=field, language=language).exists():
                            skipped += 1
                            continue
                        if not options["dry_run"]:
                            ContentTranslation.objects.create(content_type=ct, object_id=vacancy.pk, field_name=field, language=language, text=text, status="review", source_hash=fingerprint(original))
                        count += 1
            if options["dry_run"]:
                transaction.set_rollback(True)
        self.stdout.write(f"{ 'Would add' if options['dry_run'] else 'Added' }: {count}; existing preserved: {skipped}")
