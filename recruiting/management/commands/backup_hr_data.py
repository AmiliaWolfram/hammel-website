import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Erstellt eine konsistente SQLite-Sicherung inklusive hochgeladener Dokumente."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", default=None,
                            help="Verzeichnis fuer Backups (Standard: neben dem Projekt)")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("Dieses Backup unterstuetzt nur SQLite. Fuer PostgreSQL pg_dump verwenden.")
        db_path = Path(database["NAME"]).resolve()
        if not db_path.is_file():
            raise CommandError(f"Datenbank nicht gefunden: {db_path}")
        base = Path(settings.BASE_DIR).resolve()
        output = Path(options["output_dir"]).expanduser().resolve() if options["output_dir"] else base.parent / "HAMMEL_PRIVATE_BACKUPS"
        output.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = output / f"HAMMEL_HR_BACKUP_{timestamp}.zip"
        media_root = Path(settings.MEDIA_ROOT).resolve()
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "db.sqlite3"
            with sqlite3.connect(str(db_path)) as source, sqlite3.connect(str(snapshot)) as target:
                source.backup(target)
            with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(snapshot, "db.sqlite3")
                if media_root.is_dir():
                    for file in media_root.rglob("*"):
                        if file.is_file() and not file.is_symlink():
                            archive.write(file, "media/" + file.relative_to(media_root).as_posix())
        try:
            destination.chmod(0o600)
        except OSError:
            pass
        self.stdout.write(self.style.SUCCESS(f"Backup erstellt: {destination}"))
        self.stdout.write("Enthaelt personenbezogene Daten: sicher aufbewahren, nicht in Git oder ZIP-Projektarchiven teilen.")
