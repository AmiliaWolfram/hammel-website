"""Populate missing HR language records; never replace an existing translation.

Run on a backed-up database. Network required for Google Translate via deep-translator.
The machine-generated drafts must be reviewed by HR before publication.
"""
import time
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from recruiting.models import Vacancy, HRTextBlock, HRTip, VacancyDepartment, ApplicationDepartment
from translations.models import ContentTranslation
from translations.services import fingerprint

LANGUAGES = {'en': 'english', 'fr': 'french', 'es': 'spanish', 'it': 'italian'}
SOURCES = (
    (Vacancy, ('title', 'introduction', 'responsibilities', 'requirements', 'hard_skills', 'soft_skills', 'benefits')),
    (HRTextBlock, ('text',)),
    (HRTip, ('title', 'body')),
    (VacancyDepartment, ('name',)),
    (ApplicationDepartment, ('name',)),
)

class Command(BaseCommand):
    help = 'Complete missing EN/FR/ES/IT HR translations. Existing records are never changed.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only count missing fields; no network or writes')
        parser.add_argument('--limit', type=int, default=0, help='Optional limit for a test run')
        parser.add_argument('--delay', type=float, default=0.3, help='Seconds between remote requests')

    def handle(self, *args, **opts):
        pending = []
        for model, fields in SOURCES:
            ct = ContentType.objects.get_for_model(model)
            for obj in model.objects.order_by('pk').iterator():
                for field in fields:
                    source = str(getattr(obj, field, '') or '').strip()
                    if not source:
                        continue
                    for lang in LANGUAGES:
                        if not ContentTranslation.objects.filter(content_type=ct, object_id=obj.pk, field_name=field, language=lang).exists():
                            pending.append((obj, ct, field, source, lang))
        self.stdout.write(f'Missing translation fields: {len(pending)}')
        if opts['dry_run']:
            self.stdout.write('Dry run: no data changed, no translation service contacted.')
            return
        if opts['limit'] > 0:
            pending = pending[:opts['limit']]
        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:
            raise CommandError('Install dependency first: python -m pip install deep-translator') from exc
        translators = {lang: GoogleTranslator(source='de', target=lang) for lang in LANGUAGES}
        cache = {}
        created = failed = 0
        for i, (obj, ct, field, source, lang) in enumerate(pending, 1):
            try:
                key = (lang, source)
                if key not in cache:
                    # The translator limits input length; translate separate lines and
                    # split oversized lines on sentence boundaries.
                    lines = source.splitlines()
                    translated_lines = []
                    for line in lines:
                        if not line.strip():
                            translated_lines.append('')
                            continue
                        pieces = []
                        while len(line) > 4000:
                            cut = line.rfind('. ', 0, 4000)
                            if cut < 500:
                                cut = 3900
                            else:
                                cut += 1
                            pieces.append(line[:cut]); line = line[cut:].lstrip()
                        pieces.append(line)
                        translated_lines.append(' '.join(translators[lang].translate(p) for p in pieces))
                        time.sleep(max(0, opts['delay']))
                    cache[key] = '\n'.join(translated_lines)
                result = cache[key].strip()
                if not result or result == source:
                    raise ValueError('Empty or unchanged translation returned')
                with transaction.atomic():
                    _, was_created = ContentTranslation.objects.get_or_create(
                        content_type=ct, object_id=obj.pk, field_name=field, language=lang,
                        defaults={'text': result, 'status': 'review', 'source_hash': fingerprint(source)},
                    )
                created += int(was_created)
                if i % 25 == 0:
                    self.stdout.write(f'Processed {i}/{len(pending)}; added {created}; failed {failed}')
            except Exception as exc:
                failed += 1
                self.stderr.write(f'FAILED {obj._meta.label} #{obj.pk} {field}/{lang}: {exc}')
        self.stdout.write(self.style.SUCCESS(f'Added: {created}; failed: {failed}; existing translations preserved.'))
        if failed:
            raise CommandError('Some translations failed. Rerun this command; saved entries will be skipped.')
