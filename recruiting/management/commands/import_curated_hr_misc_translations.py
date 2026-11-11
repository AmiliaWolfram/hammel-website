"""Non-destructive import of reviewed HR tips and department names."""
import json
from pathlib import Path
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from recruiting.models import HRTip, VacancyDepartment, ApplicationDepartment
from translations.models import ContentTranslation
from translations.services import fingerprint

MODELS = {"hrtip": HRTip, "vacancydepartment": VacancyDepartment, "applicationdepartment": ApplicationDepartment}

class Command(BaseCommand):
    help = "Import curated HR tips and department translations without overwriting existing entries."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        path = Path(__file__).resolve().parents[2] / "data" / "curated_hr_misc_translations.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        added = preserved = skipped = 0
        with transaction.atomic():
            for row in rows:
                cls = MODELS[row["model"]]
                obj = cls.objects.filter(pk=row["pk"]).first()
                if obj is None or not str(getattr(obj, row["field"], "")).strip():
                    skipped += 1
                    continue
                ct = ContentType.objects.get_for_model(cls)
                criteria = dict(content_type=ct, object_id=obj.pk, field_name=row["field"], language=row["language"])
                if ContentTranslation.objects.filter(**criteria).exists():
                    preserved += 1
                    continue
                if not options["dry_run"]:
                    ContentTranslation.objects.create(**criteria, text=row["text"], status="review", source_hash=fingerprint(getattr(obj, row["field"])))
                added += 1
            if options["dry_run"]:
                transaction.set_rollback(True)
        self.stdout.write(f"{'Would add' if options['dry_run'] else 'Added'}: {added}; existing preserved: {preserved}; missing source: {skipped}")
