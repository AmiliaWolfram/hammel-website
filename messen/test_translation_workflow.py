"""Regression tests for the shared Messen / News translation workflow."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseBadRequest
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from .staff_views import _save_language_review, _translation_editor_rows


class ReviewActionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.item = SimpleNamespace(pk=12, published=False, language_visibility={})
        self.item.save = self._save
        self.saved_fields = []

    def _save(self, update_fields):
        self.saved_fields.append(list(update_fields))

    @patch("messen.staff_views.messages.success")
    def test_visibility_save_preserves_language_choices(self, success):
        request = self.factory.post(
            "/staff/messen/12/sprache/review/",
            {"visibility_action": "save", "visible_languages": ["en", "it"]},
        )
        with patch("messen.staff_views.redirect") as redirect:
            _save_language_review(request, self.item, "messen_language_editor", "Messe", ["published", "updated_at"])
        self.assertEqual(
            self.item.language_visibility,
            {"en": True, "fr": False, "es": False, "it": True},
        )
        self.assertEqual(self.saved_fields, [["language_visibility"]])
        redirect.assert_called_once_with("messen_language_editor", pk=12, lang="review")
        success.assert_called_once()

    def test_publication_requires_confirmation(self):
        request = self.factory.post("/", {"publication_action": "publish"})
        response = _save_language_review(request, self.item, "news_language_editor", "Beitrag", ["published"])
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertFalse(self.item.published)
        self.assertEqual(self.saved_fields, [])

    def test_invalid_publication_action_does_not_save(self):
        request = self.factory.post("/", {"publication_confirm": "on", "publication_action": "delete"})
        response = _save_language_review(request, self.item, "news_language_editor", "Beitrag", ["published"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.saved_fields, [])

    @patch("messen.staff_views.messages.success")
    @patch("messen.staff_views.redirect")
    def test_messen_publish_updates_timestamp(self, redirect, success):
        request = self.factory.post("/", {"publication_confirm": "on", "publication_action": "publish"})
        _save_language_review(request, self.item, "messen_language_editor", "Messe", ["published", "updated_at"])
        self.assertTrue(self.item.published)
        self.assertEqual(self.saved_fields, [["published", "updated_at"]])

    @patch("messen.staff_views.messages.success")
    @patch("messen.staff_views.redirect")
    def test_news_unpublish_only_updates_published(self, redirect, success):
        self.item.published = True
        request = self.factory.post("/", {"publication_confirm": "on", "publication_action": "unpublish"})
        _save_language_review(request, self.item, "news_language_editor", "Beitrag", ["published"])
        self.assertFalse(self.item.published)
        self.assertEqual(self.saved_fields, [["published"]])


class TranslationRowsTests(SimpleTestCase):
    def test_review_rows_detect_missing_and_stale_translations(self):
        item = SimpleNamespace(title="Original")
        field = SimpleNamespace(name="title", verbose_name="Titel")
        translations = {
            ("en", "title"): SimpleNamespace(text="English", status="published", source_hash="old"),
            ("it", "title"): SimpleNamespace(text="Italiano", status="review", source_hash="current"),
        }
        rows = _translation_editor_rows(item, [field], translations, "review", lambda value: "current")
        self.assertEqual(len(rows), 1)
        self.assertEqual([cell["code"] for cell in rows[0]["cells"]], ["en", "fr", "es", "it"])
        self.assertTrue(rows[0]["cells"][0]["stale"])
        self.assertEqual(rows[0]["cells"][1]["text"], "")
        self.assertFalse(rows[0]["cells"][3]["stale"])

    def test_single_language_row(self):
        item = SimpleNamespace(title="Original")
        field = SimpleNamespace(name="title", verbose_name="Titel")
        rows = _translation_editor_rows(item, [field], {}, "es", lambda value: "hash")
        self.assertEqual(rows[0]["status"], "draft")
        self.assertEqual(rows[0]["original"], "Original")
        self.assertNotIn("cells", rows[0])


class LanguageRoutesTests(SimpleTestCase):
    def test_messen_and_news_review_urls(self):
        self.assertEqual(reverse("messen_language_editor", args=[12, "review"]), "/staff/messen/12/sprachen/review/")
        self.assertEqual(reverse("news_language_editor", args=[12, "review"]), "/staff/news/12/sprache/review/")
