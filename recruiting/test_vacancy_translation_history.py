"""Regression tests for append-only vacancy translation history."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from recruiting.models import HREditLog, Vacancy, VacancyDepartment
from translations.models import ContentTranslation
from translations.services import fingerprint


class VacancyTranslationHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="stage24_editor", password="test-password")
        self.user.user_permissions.add(*Permission.objects.filter(content_type__app_label="recruiting"))
        self.client.force_login(self.user)
        self.department, _ = VacancyDepartment.objects.get_or_create(name="Stage24 Test")
        self.vacancy = Vacancy.objects.create(
            title="Original", category="job", department=self.department,
            location="Bad Salzungen", introduction="Einleitung",
            responsibilities="Aufgaben", requirements="Erfahrung",
            hard_skills="Kenntnisse", soft_skills="Team", benefits="Vorteile",
        )
        self.url = reverse("translation_autosave", args=["recruiting", "vacancy", self.vacancy.pk])
        self.ct = ContentType.objects.get_for_model(Vacancy)

    def save(self, language, text):
        return self.client.post(self.url, {"language": language, "field": "title", "text": text})

    def test_autosave_records_old_and_new_translation_with_author(self):
        self.assertEqual(self.save("en", "First title").status_code, 200)
        self.assertEqual(self.save("en", "Revised title").status_code, 200)
        history = list(HREditLog.objects.filter(vacancy=self.vacancy, action="translation").order_by("pk"))
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1].user_id, self.user.pk)
        self.assertIsNotNone(history[1].created_at)
        self.assertIn({"field": "EN · title", "old": "First title", "new": "Revised title"}, history[1].changes)

    def test_unchanged_autosave_does_not_duplicate_history(self):
        self.save("fr", "Bonjour")
        self.save("fr", "Bonjour")
        self.assertEqual(HREditLog.objects.filter(vacancy=self.vacancy, action="translation").count(), 1)

    def test_all_four_languages_have_separate_history(self):
        for language, text in (("en", "English"), ("fr", "Français"),
                               ("es", "Español"), ("it", "Italiano")):
            self.assertEqual(self.save(language, text).status_code, 200)
        history = HREditLog.objects.filter(vacancy=self.vacancy, action="translation")
        self.assertEqual(history.count(), 4)
        self.assertEqual({log.changes[0]["field"].split(" · ")[0] for log in history},
                         {"EN", "FR", "ES", "IT"})
        self.assertEqual(ContentTranslation.objects.filter(
            content_type=self.ct, object_id=self.vacancy.pk, field_name="title").count(), 4)

    def test_status_downgrade_of_stale_translation_is_audited(self):
        item = ContentTranslation.objects.create(
            content_type=self.ct, object_id=self.vacancy.pk, language="es",
            field_name="title", text="Antiguo", status="published",
            source_hash=fingerprint("Previous original"), updated_by=self.user,
        )
        response = self.save("es", "Antiguo")
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, "review")
        history = HREditLog.objects.get(vacancy=self.vacancy, action="translation")
        self.assertIn({"field": "ES · title (Status)", "old": "published", "new": "review"}, history.changes)

    def test_invalid_autosave_does_not_create_history(self):
        response = self.client.post(self.url, {"language": "de", "field": "title", "text": "No"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(HREditLog.objects.filter(vacancy=self.vacancy).exists())
