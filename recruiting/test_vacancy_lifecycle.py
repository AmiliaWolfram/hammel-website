"""End-to-end database tests for the German Stellen editor and translations.

Run with: python manage.py test recruiting.test_vacancy_lifecycle
All database changes happen in Django's disposable test database.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from recruiting.models import HREditLog, Vacancy, VacancyDepartment
from translations.models import ContentTranslation
from translations.services import fingerprint


class VacancyLifecycleTests(TestCase):
    def setUp(self):
        self.editor = get_user_model().objects.create_user(
            username="stage21_editor", password="test-only-password"
        )
        self.editor.user_permissions.add(
            *Permission.objects.filter(content_type__app_label="recruiting")
        )
        self.client.force_login(self.editor)
        self.department, _ = VacancyDepartment.objects.get_or_create(
            name="Stage21 Vertrieb"
        )
        self.vacancy = Vacancy.objects.create(
            title="Originalstelle", category="job", department=self.department,
            location="Bad Salzungen", employment_type="Vollzeit",
            introduction="Einleitung vorher", responsibilities="Aufgabe vorher",
            requirements="Erfahrung", hard_skills="Office", soft_skills="Teamgeist",
            benefits="Weiterbildung",
        )
        self.ct = ContentType.objects.get_for_model(Vacancy)

    def edit_payload(self, **overrides):
        payload = {
            "title": self.vacancy.title, "category": "job",
            "department": str(self.department.pk), "location": "Bad Salzungen",
            "employment_type": "Vollzeit", "introduction": self.vacancy.introduction,
            "responsibilities": self.vacancy.responsibilities,
            "requirements": self.vacancy.requirements,
            "hard_skills": self.vacancy.hard_skills,
            "soft_skills": self.vacancy.soft_skills, "benefits": self.vacancy.benefits,
        }
        payload.update(overrides)
        return payload

    def translation(self, language, field, text, status="review"):
        return ContentTranslation.objects.create(
            content_type=self.ct, object_id=self.vacancy.pk,
            language=language, field_name=field, text=text,
            status=status, source_hash=fingerprint(getattr(self.vacancy, field)),
            updated_by=self.editor,
        )

    def test_edit_preserves_existing_translations_and_publication(self):
        en = self.translation("en", "title", "English original", "published")
        fr = self.translation("fr", "title", "Titre français", "review")
        self.vacancy.published = True
        self.vacancy.visible_languages = ["de", "en"]
        self.vacancy.save(update_fields=["published", "visible_languages"])
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]),
            self.edit_payload(title="Aktualisierte Stelle"),
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.title, "Aktualisierte Stelle")
        self.assertTrue(self.vacancy.published)
        self.assertEqual(self.vacancy.visible_languages, ["de", "en"])
        en.refresh_from_db()
        fr.refresh_from_db()
        self.assertEqual((en.text, en.status), ("English original", "published"))
        self.assertEqual((fr.text, fr.status), ("Titre français", "review"))
        self.assertNotEqual(en.source_hash, fingerprint(self.vacancy.title))
        self.assertEqual(
            ContentTranslation.objects.filter(
                content_type=self.ct, object_id=self.vacancy.pk,
                field_name="title",
            ).count(), 2
        )

    def test_german_edit_creates_audit_record(self):
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]),
            self.edit_payload(title="Neuer Titel"),
        )
        self.assertEqual(response.status_code, 302)
        log = HREditLog.objects.filter(
            vacancy=self.vacancy, action="updated"
        ).latest("pk")
        self.assertEqual(log.user_id, self.editor.pk)
        self.assertTrue(any(
            item["old"] == "Originalstelle" and item["new"] == "Neuer Titel"
            for item in log.changes
        ))

    def test_language_autosave_does_not_delete_other_languages(self):
        en = self.translation("en", "title", "English")
        fr = self.translation("fr", "title", "Français")
        url = reverse("translation_autosave", args=[
            "recruiting", "vacancy", self.vacancy.pk
        ])
        response = self.client.post(url, {
            "language": "en", "field": "title", "text": "Updated English",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        en.refresh_from_db()
        fr.refresh_from_db()
        self.assertEqual(en.text, "Updated English")
        self.assertEqual(fr.text, "Français")

    def test_unconfirmed_publication_does_not_change_status(self):
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review",
            {"publication_action": "publish"},
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertFalse(self.vacancy.published)

    def test_user_without_change_permission_cannot_edit(self):
        other = get_user_model().objects.create_user(
            username="stage21_no_permission", password="test-only-password"
        )
        self.client.force_login(other)
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]),
            self.edit_payload(title="Unberechtigt geändert"),
        )
        self.assertEqual(response.status_code, 403)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.title, "Originalstelle")
        self.assertFalse(HREditLog.objects.filter(vacancy=self.vacancy).exists())

    def test_german_edit_preserves_all_four_language_versions(self):
        languages = {"en": "English", "fr": "Français", "es": "Español", "it": "Italiano"}
        records = {
            code: self.translation(code, "title", text, "published")
            for code, text in languages.items()
        }
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]),
            self.edit_payload(title="Neuer deutscher Titel"),
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.title, "Neuer deutscher Titel")
        for code, record in records.items():
            with self.subTest(language=code):
                record.refresh_from_db()
                self.assertEqual(record.text, languages[code])
                self.assertEqual(record.status, "published")
                self.assertNotEqual(record.source_hash, fingerprint(self.vacancy.title))

    def test_only_changed_german_fields_become_stale(self):
        title = self.translation("en", "title", "Title", "published")
        benefits = self.translation("en", "benefits", "Benefits", "published")
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]),
            self.edit_payload(title="Neuer Titel"),
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        title.refresh_from_db()
        benefits.refresh_from_db()
        self.assertNotEqual(title.source_hash, fingerprint(self.vacancy.title))
        self.assertEqual(benefits.source_hash, fingerprint(self.vacancy.benefits))
        self.assertEqual(benefits.text, "Benefits")

    def test_autosave_one_language_preserves_other_three(self):
        records = {
            code: self.translation(code, "title", text)
            for code, text in (
                ("en", "English"), ("fr", "Français"),
                ("es", "Español"), ("it", "Italiano")
            )
        }
        response = self.client.post(
            reverse("translation_autosave", args=[
                "recruiting", "vacancy", self.vacancy.pk
            ]),
            {"language": "es", "field": "title", "text": "Título actualizado"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        for code, record in records.items():
            with self.subTest(language=code):
                record.refresh_from_db()
                self.assertEqual(
                    record.text,
                    "Título actualizado" if code == "es" else {
                        "en": "English", "fr": "Français", "it": "Italiano"
                    }[code],
                )

    def test_readiness_summary_marks_stale_and_missing_languages(self):
        from recruiting.views import _vacancy_translation_summary
        required = [("title", self.vacancy.title)]
        self.translation("en", "title", "English", "published")
        self.translation("fr", "title", "Français", "review")
        self.translation("es", "title", "Español", "published")
        self.vacancy.title = "Neuer deutscher Titel"
        self.vacancy.save(update_fields=["title"])
        translations = list(ContentTranslation.objects.filter(
            content_type=self.ct, object_id=self.vacancy.pk
        ))
        rows = _vacancy_translation_summary(
            required=[("title", self.vacancy.title)],
            translations=translations,
            languages=(("de", "Deutsch"), ("en", "English"),
                       ("fr", "Français"), ("es", "Español"), ("it", "Italiano")),
            fingerprint=fingerprint,
        )
        self.assertEqual([row["code"] for row in rows], ["en", "fr", "es", "it"])
        self.assertEqual([row["stale"] for row in rows], [1, 1, 1, 0])
        self.assertEqual(rows[3]["missing"], 1)
        self.assertTrue(all(not row["complete"] for row in rows))

    def test_visibility_change_on_published_vacancy_is_audited(self):
        self.vacancy.published = True
        self.vacancy.visible_languages = ["de"]
        self.vacancy.save(update_fields=["published", "visible_languages"])
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review",
            {"publication_action": "languages", "visible_languages": ["de", "en", "fr"]},
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.visible_languages, ["de", "en", "fr"])
        log = HREditLog.objects.filter(
            vacancy=self.vacancy, action="update", detail="Sprachsichtbarkeit geändert"
        ).get()
        self.assertEqual(log.user_id, self.editor.pk)
        self.assertEqual(log.changes[0]["old"], "de")
        self.assertEqual(log.changes[0]["new"], "de, en, fr")
        self.assertIsNotNone(log.created_at)

    def test_identical_visibility_does_not_create_duplicate_audit(self):
        self.vacancy.published = True
        self.vacancy.visible_languages = ["de", "en"]
        self.vacancy.save(update_fields=["published", "visible_languages"])
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review",
            {"publication_action": "languages", "visible_languages": ["de", "en"]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(HREditLog.objects.filter(
            vacancy=self.vacancy, detail="Sprachsichtbarkeit geändert"
        ).exists())

    def test_draft_vacancy_cannot_expose_translated_languages(self):
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review",
            {"publication_action": "languages", "visible_languages": ["de", "en", "fr"]},
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertFalse(self.vacancy.published)
        self.assertEqual(self.vacancy.visible_languages, [])
        self.assertFalse(HREditLog.objects.filter(vacancy=self.vacancy).exists())

    def test_unconfirmed_unpublish_preserves_publication_and_history(self):
        self.vacancy.published = True
        self.vacancy.visible_languages = ["de", "en"]
        self.vacancy.save(update_fields=["published", "visible_languages"])
        response = self.client.post(
            reverse("hr_edit", args=["vacancy", self.vacancy.pk]) + "?step=review",
            {"publication_action": "unpublish"},
        )
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertTrue(self.vacancy.published)
        self.assertEqual(self.vacancy.visible_languages, ["de", "en"])
        self.assertFalse(HREditLog.objects.filter(vacancy=self.vacancy).exists())
