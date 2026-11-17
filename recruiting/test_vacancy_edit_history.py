"""Tests for German-original vacancy audit diff preparation."""
from types import SimpleNamespace
from django.test import SimpleTestCase
from recruiting.views import _vacancy_edit_changes


class VacancyEditChangesTests(SimpleTestCase):
    def test_changed_fields_preserve_labels_and_previous_values(self):
        form = SimpleNamespace(
            changed_data=["title", "introduction"],
            fields={
                "title": SimpleNamespace(label="Stellenbezeichnung"),
                "introduction": SimpleNamespace(label="Einleitung"),
            },
        )
        instance = SimpleNamespace(title="Neue Stelle", introduction="Neuer Text")
        changes = _vacancy_edit_changes(
            form, instance, {"title": "Alte Stelle", "introduction": "Alter Text"}
        )
        self.assertEqual(changes, [
            {"field": "Stellenbezeichnung", "old": "Alte Stelle", "new": "Neue Stelle"},
            {"field": "Einleitung", "old": "Alter Text", "new": "Neuer Text"},
        ])

    def test_empty_changed_data_produces_empty_history_diff(self):
        form = SimpleNamespace(changed_data=[], fields={})
        self.assertEqual(_vacancy_edit_changes(form, SimpleNamespace(), {}), [])

    def test_empty_values_and_missing_previous_values_preserve_original_behavior(self):
        form = SimpleNamespace(
            changed_data=["benefits"],
            fields={"benefits": SimpleNamespace(label=None)},
        )
        instance = SimpleNamespace(benefits=None)
        self.assertEqual(_vacancy_edit_changes(form, instance, {}), [
            {"field": "benefits", "old": "", "new": ""}
        ])

    def test_only_changed_fields_appear_in_audit(self):
        form = SimpleNamespace(
            changed_data=["title"],
            fields={"title": SimpleNamespace(label="Titel"),
                    "published": SimpleNamespace(label="Veröffentlichen")},
        )
        instance = SimpleNamespace(title="Neu", published=True)
        result = _vacancy_edit_changes(form, instance, {"title": "Alt"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["field"], "Titel")
