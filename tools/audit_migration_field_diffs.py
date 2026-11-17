"""Read-only comparison of current Django fields with migration state.

Run from the project root: python tools/audit_migration_field_diffs.py
Does not generate migrations or modify database records/schema.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.apps import apps
from django.db import connection
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations.fields import AlterField
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState

TARGETS = ("messen", "partners", "recruiting")
MISSING = object()


def safe_repr(value):
    """Human-readable, bounded representation for diagnostics only."""
    if value is MISSING:
        return "<not specified>"
    if callable(value):
        return getattr(value, "__module__", "") + "." + getattr(value, "__qualname__", repr(value))
    result = repr(value)
    return result if len(result) <= 240 else result[:237] + "..."


def field_signature(field):
    _, path, args, kwargs = field.deconstruct()
    return path, args, kwargs


def main():
    loader = MigrationLoader(connection, ignore_no_migrations=True)
    historical_state = loader.project_state()
    current_state = ProjectState.from_apps(apps)
    detector = MigrationAutodetector(
        historical_state, current_state,
        NonInteractiveMigrationQuestioner(specified_apps=set(TARGETS)),
    )
    proposed = detector.changes(graph=loader.graph, trim_to_apps=set(TARGETS))
    print("HAMMEL DE – READ-ONLY FIELD DIFFERENCES")
    print("Database engine:", connection.vendor)
    print("No database or migration writes will be performed.\n")
    total = 0
    for label in TARGETS:
        print("[" + label + "]")
        count = 0
        for migration in proposed.get(label, []):
            for operation in migration.operations:
                if not isinstance(operation, AlterField):
                    print("  OTHER PROPOSED OPERATION:", type(operation).__name__, operation)
                    continue
                model_name = operation.model_name.lower()
                name = operation.name
                state_model = historical_state.models.get((label, model_name))
                current_model = apps.get_model(label, model_name)
                if state_model is None or current_model is None:
                    print("  MISSING MODEL:", model_name)
                    continue
                old_field = state_model.fields.get(name)
                try:
                    new_field = current_model._meta.get_field(name)
                except Exception as exc:
                    print("  FIELD NOT FOUND:", model_name, name, type(exc).__name__)
                    continue
                if old_field is None:
                    print("  FIELD NOT IN MIGRATION STATE:", model_name, name)
                    continue
                old_path, old_args, old_kwargs = field_signature(old_field)
                new_path, new_args, new_kwargs = field_signature(new_field)
                print("  " + model_name + "." + name)
                if old_path != new_path:
                    print("    type: " + old_path + " -> " + new_path)
                if old_args != new_args:
                    print("    positional args: " + safe_repr(old_args) + " -> " + safe_repr(new_args))
                keys = sorted(set(old_kwargs) | set(new_kwargs))
                differences = 0
                for key in keys:
                    old_value = old_kwargs.get(key, MISSING)
                    new_value = new_kwargs.get(key, MISSING)
                    if old_value != new_value:
                        differences += 1
                        print("    " + key + ": " + safe_repr(old_value) + " -> " + safe_repr(new_value))
                if not differences and old_path == new_path and old_args == new_args:
                    print("    No simple deconstruct difference; inspect migration state manually")
                count += 1
        total += count
        print("  Proposed AlterField operations:", count, "\n")
    print("TOTAL:", total, "AlterField operations")
    print("AUDIT ONLY – no migrations generated/applied, no data changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
