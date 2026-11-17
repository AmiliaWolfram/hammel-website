"""Read-only migration and primary-key audit for HAMMEL DE.

Run from project root with active venv:
    python tools/audit_model_migration_ids.py
No migration generation, schema writes, or data writes are performed.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.apps import apps
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState

TARGETS = ('messen', 'partners', 'recruiting')


def main():
    loader = MigrationLoader(connection, ignore_no_migrations=True)
    recorded = set(loader.applied_migrations)
    print('HAMMEL DE – READ-ONLY MODEL / MIGRATION AUDIT')
    print('Database engine:', connection.vendor)
    print('Default auto field:', django.conf.settings.DEFAULT_AUTO_FIELD)
    print()
    disk_state = loader.project_state()
    current_state = ProjectState.from_apps(apps)
    detector = MigrationAutodetector(
        disk_state, current_state,
        NonInteractiveMigrationQuestioner(specified_apps=set(TARGETS)),
    )
    proposed = detector.changes(graph=loader.graph, trim_to_apps=set(TARGETS))
    for label in TARGETS:
        models = list(apps.get_app_config(label).get_models())
        print(f'[{label}] {len(models)} models')
        for model in models:
            pk = model._meta.pk
            historical = disk_state.models.get((label, model._meta.model_name))
            historical_pk = None
            if historical:
                for name, field in historical.fields.items():
                    if getattr(field, 'primary_key', False):
                        historical_pk = (name, field.__class__.__name__)
                        break
            live = (pk.name, pk.__class__.__name__)
            if historical_pk != live:
                print(f'  PK DRIFT: {model.__name__}: migrations={historical_pk}, model={live}')
        migrations = proposed.get(label, [])
        if not migrations:
            print('  No model-vs-migration changes proposed')
        else:
            for migration in migrations:
                print('  PROPOSED (NOT APPLIED):', migration.name)
                for op in migration.operations:
                    print('   ', type(op).__name__, str(op)[:250])
        disk_migrations = {key for key in loader.disk_migrations if key[0] == label}
        pending = sorted(disk_migrations - recorded)
        print('  Pending existing migrations:', pending if pending else 'none')
        print()
    print('AUDIT ONLY: no migrations generated or applied, no data modified.')
    return 1 if any(proposed.get(label) for label in TARGETS) else 0


if __name__ == '__main__':
    raise SystemExit(main())
