"""Database-backed regression tests for Messen and News translation editors."""

from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from messen.models import Messe, MesseTranslationChange, NewsArticle, NewsTranslationChange
from translations.models import ContentTranslation


class TranslationEditorIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = get_user_model().objects.create_superuser(
            username="translation_test_editor", email="editor@example.invalid", password="test-password"
        )
        cls.messe = Messe.objects.create(
            title="Original Messe", start_date=date(2027, 5, 10),
            end_date=date(2027, 5, 12), city="Berlin",
        )
        cls.news = NewsArticle.objects.create(
            title="Original News", published_at=date(2027, 5, 10),
            teaser="Original teaser", body="Original body",
        )

    def setUp(self):
        self.client.force_login(self.editor)

    def url(self, item, lang="en"):
        name = "messen_language_editor" if isinstance(item, Messe) else "news_language_editor"
        return reverse(name, args=[item.pk, lang])

    def translation(self, item, field="title", lang="en"):
        return ContentTranslation.objects.get(
            content_type=ContentType.objects.get_for_model(item),
            object_id=item.pk, field_name=field, language=lang,
        )

    def test_save_creates_translation_and_audit_for_both_editors(self):
        for item, audit_model, relation in (
            (self.messe, MesseTranslationChange, "messe"),
            (self.news, NewsTranslationChange, "article"),
        ):
            with self.subTest(item=item.__class__.__name__):
                response = self.client.post(self.url(item), {
                    "translation_title": "Translated title", "status_title": "published",
                })
                self.assertEqual(response.status_code, 302)
                translation = self.translation(item)
                self.assertEqual(translation.text, "Translated title")
                self.assertEqual(translation.status, "published")
                self.assertEqual(translation.updated_by_id, self.editor.pk)
                self.assertTrue(audit_model.objects.filter(**{
                    relation: item, "field_name": "title", "new_text": "Translated title"
                }).exists())

    def test_status_change_is_audited_without_duplicate_translation(self):
        self.client.post(self.url(self.news), {
            "translation_title": "English title", "status_title": "draft",
        })
        self.client.post(self.url(self.news), {
            "translation_title": "English title", "status_title": "review",
        })
        self.assertEqual(self.translation(self.news).status, "review")
        self.assertEqual(ContentTranslation.objects.filter(
            content_type=ContentType.objects.get_for_model(self.news),
            object_id=self.news.pk, field_name="title", language="en",
        ).count(), 1)
        self.assertTrue(NewsTranslationChange.objects.filter(
            article=self.news, field_name="title", old_status="draft", new_status="review"
        ).exists())

    def test_changed_original_marks_translation_stale(self):
        self.client.post(self.url(self.news), {
            "translation_title": "English title", "status_title": "published",
        })
        self.news.title = "Changed German title"
        self.news.save(update_fields=["title"])
        response = self.client.get(self.url(self.news))
        self.assertEqual(response.status_code, 200)
        title_row = next(row for row in response.context["rows"] if row["name"] == "title")
        self.assertTrue(title_row["stale"])

    def test_stale_translation_cannot_remain_published_without_confirmation(self):
        self.client.post(self.url(self.news), {
            "translation_title": "English title", "status_title": "published",
        })
        self.news.title = "Updated German original"
        self.news.save(update_fields=["title"])
        self.client.post(self.url(self.news), {
            "translation_title": "English title", "status_title": "published",
        })
        self.assertEqual(self.translation(self.news).status, "review")

    def test_audit_failure_rolls_back_translation_save(self):
        with patch.object(NewsTranslationChange.objects, "create", side_effect=IntegrityError("audit failure")):
            with self.assertRaises(IntegrityError):
                self.client.post(self.url(self.news), {
                    "translation_title": "Must rollback", "status_title": "published",
                })
        self.assertFalse(ContentTranslation.objects.filter(
            content_type=ContentType.objects.get_for_model(self.news),
            object_id=self.news.pk, field_name="title", language="en",
        ).exists())

    def test_review_visibility_persists(self):
        response = self.client.post(self.url(self.messe, "review"), {
            "visibility_action": "save", "visible_languages": ["en", "it"],
        })
        self.assertEqual(response.status_code, 302)
        self.messe.refresh_from_db()
        self.assertEqual(self.messe.language_visibility, {
            "en": True, "fr": False, "es": False, "it": True,
        })

    def test_non_editor_cannot_save_translations(self):
        viewer = get_user_model().objects.create_user(username="translation_viewer", password="test-password")
        self.client.force_login(viewer)
        for item in (self.messe, self.news):
            with self.subTest(item=item.__class__.__name__):
                response = self.client.post(self.url(item), {
                    "translation_title": "Forbidden", "status_title": "published",
                })
                self.assertEqual(response.status_code, 403)
