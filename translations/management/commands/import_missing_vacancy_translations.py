import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from recruiting.models import Vacancy
from translations.models import ContentTranslation


class Command(BaseCommand):
    help = "Import missing vacancy translations without overwriting existing data."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show proposed changes without writing anything')

    def handle(self, *args, **options):
        source = Path(__file__).resolve().parents[2] / 'data' / 'vacancy_title_translations.json'
        data = json.loads(source.read_text(encoding='utf-8'))
        titles = list(Vacancy.objects.values_list('pk', 'title'))
        counts = Counter(title for _, title in titles)
        by_title = {title: pk for pk, title in titles if counts[title] == 1}
        ct = ContentType.objects.get_for_model(Vacancy)
        pending = []
        skipped = Counter()
        for item in data:
            title = item['original_title']
            if title not in by_title:
                skipped['missing_or_ambiguous_vacancy'] += 1
                continue
            pk = by_title[title]
            if ContentTranslation.objects.filter(content_type=ct, object_id=pk, field_name=item['field'], language=item['language']).exists():
                skipped['already_exists'] += 1
                continue
            pending.append((pk, title, item))
        self.stdout.write(f"Found {len(pending)} missing translations; skipped: {dict(skipped)}")
        if options['dry_run']:
            return
        if connection.vendor != 'sqlite':
            raise CommandError('Automatic backup is supported for SQLite only. For PostgreSQL, create and verify a pg_dump backup before importing; then use the SQLite-independent --dry-run to inspect changes. No data was changed.')
        db_name = settings.DATABASES['default']['NAME']
        db_path = Path(db_name)
        if not db_path.is_file():
            raise CommandError(f'Active SQLite database not found: {db_path}')
        backups = Path(settings.BASE_DIR) / 'database_backups'
        backups.mkdir(exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup = backups / f'pre_translation_import_{stamp}.sqlite3'
        connection.close()
        with sqlite3.connect(str(db_path)) as live, sqlite3.connect(str(backup)) as copy:
            live.backup(copy)
            integrity = copy.execute('PRAGMA integrity_check').fetchone()[0]
            if integrity != 'ok':
                backup.unlink(missing_ok=True)
                raise CommandError(f'Backup failed integrity check: {integrity}')
        self.stdout.write(self.style.SUCCESS(f'Verified backup: {backup}'))
        created = 0
        with transaction.atomic():
            for pk, title, item in pending:
                _, was_created = ContentTranslation.objects.get_or_create(
                    content_type=ct, object_id=pk, field_name=item['field'], language=item['language'],
                    defaults={'text': item['text'], 'status': 'review', 'source_hash': hashlib.sha256(title.encode('utf-8')).hexdigest()},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Added {created} translations; existing records unchanged.'))
