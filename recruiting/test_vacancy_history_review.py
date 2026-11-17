"""Integration tests for translation history shown on Stellen → Prüfung."""
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from recruiting.models import HREditLog, Vacancy, VacancyDepartment


class VacancyHistoryReviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage25_reviewer", password="test-password"
        )
        self.user.user_permissions.add(
            *Permission.objects.filter(content_type__app_label="recruiting")
        )
        self.client.force_login(self.user)
        department, _ = VacancyDepartment.objects.get_or_create(name="Stage25")
        self.vacancy = Vacancy.objects.create(
            title="Teststelle", category="job", department=department,
            location="Bad Salzungen", introduction="Einleitung",
            responsibilities="Aufgaben", requirements="Erfahrung",
            hard_skills="Kenntnisse", soft_skills="Team", benefits="Vorteile",
        )
        self.other = Vacancy.objects.create(
            title="Andere Stelle", category="job", department=department,
            location="Bad Salzungen",
        )
        self.url = reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review"

    def add_log(self, vacancy=None, language="EN", month=None, year=None):
        log = HREditLog.objects.create(
            vacancy=vacancy or self.vacancy, user=self.user,
            action="translation", detail="Übersetzung geändert",
            changes=[{"field": language + " · title",
                      "old": "Alt", "new": "Neu"}],
        )
        if month is not None:
            HREditLog.objects.filter(pk=log.pk).update(
                created_at=timezone.make_aware(datetime(year, month, 15, 12, 0))
            )
            log.refresh_from_db()
        return log

    def test_review_contains_translation_history(self):
        log = self.add_log(language="FR")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.pk for item in response.context["history"]], [log.pk]
        )
        self.assertContains(response, "FR")

    def test_review_does_not_show_another_vacancy_history(self):
        own = self.add_log(language="ES")
        self.add_log(vacancy=self.other, language="IT")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.pk for item in response.context["history"]], [own.pk]
        )

    def test_month_and_year_filters_apply_to_translation_history(self):
        november = self.add_log(language="EN", month=11, year=2026)
        self.add_log(language="FR", month=10, year=2025)
        response = self.client.get(self.url + "&month=11&year=2026")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.pk for item in response.context["history"]], [november.pk]
        )

    def test_review_history_is_read_only(self):
        log = self.add_log(language="IT")
        before = (log.action, log.detail, log.changes, log.created_at)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        log.refresh_from_db()
        self.assertEqual(
            (log.action, log.detail, log.changes, log.created_at), before
        )
