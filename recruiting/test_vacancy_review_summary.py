"""Focused, database-free tests for the Stellen translation readiness summary."""
from types import SimpleNamespace
from django.test import SimpleTestCase
from recruiting.views import _vacancy_translation_summary


LANGUAGES = (("de", "Deutsch"), ("en", "English"), ("fr", "Français"),
             ("es", "Español"), ("it", "Italiano"))


def fingerprint(value):
    return "hash:" + value


def entry(language, field, text, source, status="published"):
    return SimpleNamespace(language=language, field_name=field, text=text,
                           source_hash=source, status=status)


class VacancyTranslationSummaryTests(SimpleTestCase):
    def test_all_published_translations_are_complete(self):
        required = [("title", "Titel"), ("benefits", "Vorteile")]
        records = [entry(code, field, "Translated", fingerprint(value))
                   for code, _ in LANGUAGES[1:] for field, value in required]
        result = _vacancy_translation_summary(required, records, LANGUAGES, fingerprint)
        self.assertEqual(len(result), 4)
        self.assertTrue(all(row["complete"] and row["percent"] == 100 for row in result))

    def test_missing_stale_and_review_are_counted_separately(self):
        required = [("title", "Titel"), ("benefits", "Vorteile"),
                    ("introduction", "Intro"), ("requirements", "Anforderungen")]
        records = [
            entry("en", "title", "Title", fingerprint("Titel")),
            entry("en", "benefits", "Benefits", "old-hash"),
            entry("en", "introduction", "Introduction", fingerprint("Intro"), "review"),
        ]
        result = _vacancy_translation_summary(required, records, LANGUAGES, fingerprint)
        english = result[0]
        self.assertEqual((english["ready"], english["stale"], english["review"], english["missing"]),
                         (1, 1, 1, 1))
        self.assertEqual(english["percent"], 25)
        self.assertFalse(english["complete"])

    def test_placeholder_is_missing(self):
        required = [("title", "Titel")]
        records = [entry("en", "title", "  TEST ", fingerprint("Titel"))]
        result = _vacancy_translation_summary(required, records, LANGUAGES, fingerprint)
        self.assertEqual(result[0]["missing"], 1)

    def test_no_required_fields_retains_original_percent_behavior(self):
        result = _vacancy_translation_summary([], [], LANGUAGES, fingerprint)
        self.assertTrue(all(row["percent"] == 100 and not row["complete"] for row in result))
