"""Run with: python manage.py test recruiting.test_hr_workflow

Uses Django's disposable test database; never touches the working HR database.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from recruiting.models import Vacancy, VacancyDepartment
from translations.models import ContentTranslation
from translations.services import fingerprint


class HRWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='hr_workflow_test', password='test-only-123')
        self.user.user_permissions.add(*Permission.objects.filter(content_type__app_label='recruiting'))
        self.client.force_login(self.user)
        self.department, _ = VacancyDepartment.objects.get_or_create(name='Vertrieb')
        self.vacancy = Vacancy.objects.create(title='Test Verkauf', category='job', department=self.department,
            location='Bad Salzungen', introduction='Wir suchen Verstärkung.',
            responsibilities='Anfragen bearbeiten', hard_skills='MS Office',
            soft_skills='Kommunikation', benefits='Gutes Team')

    def test_publication_requires_confirmation(self):
        url = reverse('hr_edit', args=['vacancy', self.vacancy.pk]) + '?step=review'
        response = self.client.post(url, {'publication_action': 'publish'})
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertFalse(self.vacancy.published)
        response = self.client.post(url, {'publication_action': 'publish', 'confirm_publication': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.vacancy.refresh_from_db()
        self.assertTrue(self.vacancy.published)

    def test_publication_blocked_if_required_text_missing(self):
        self.vacancy.introduction = ''
        self.vacancy.save()
        url = reverse('hr_edit', args=['vacancy', self.vacancy.pk]) + '?step=review'
        self.client.post(url, {'publication_action': 'publish', 'confirm_publication': 'yes'})
        self.vacancy.refresh_from_db()
        self.assertFalse(self.vacancy.published)
        self.assertContains(self.client.get(url), 'Einleitung')

    def test_translation_autosave_preserves_other_languages(self):
        url = reverse('translation_autosave', args=['recruiting', 'vacancy', self.vacancy.pk])
        response = self.client.post(url, {'language': 'en', 'field': 'title', 'text': 'Sales Specialist'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        en = ContentTranslation.objects.get(content_type=ContentType.objects.get_for_model(Vacancy),
            object_id=self.vacancy.pk, language='en', field_name='title')
        self.assertEqual(en.status, 'review')
        self.assertEqual(en.text, 'Sales Specialist')
        self.assertEqual(en.source_hash, fingerprint(self.vacancy.title))
        self.client.post(url, {'language': 'fr', 'field': 'title', 'text': 'Spécialiste commercial'})
        self.assertEqual(ContentTranslation.objects.filter(object_id=self.vacancy.pk, field_name='title').count(), 2)
        self.client.post(url, {'language': 'en', 'field': 'title', 'text': 'Sales Specialist'})
        self.assertEqual(ContentTranslation.objects.filter(object_id=self.vacancy.pk, field_name='title').count(), 2)

    def test_preview_does_not_publish(self):
        self.assertEqual(self.client.get(reverse('hr_preview', args=[self.vacancy.pk]) + '?lang=en').status_code, 200)
        self.vacancy.refresh_from_db()
        self.assertFalse(self.vacancy.published)

    def test_create_edit_and_review_roundtrip(self):
        create = reverse('hr_new', args=['vacancy'])
        self.assertEqual(self.client.get(create).status_code, 200)
        payload = {'title': 'Neue Teststelle', 'category': 'job', 'department': str(self.department.pk),
                   'location': 'Bad Salzungen', 'employment_type': 'Vollzeit',
                   'introduction': 'Wir suchen dich', 'responsibilities': 'Kunden beraten',
                   'requirements': 'Erfahrung', 'hard_skills': 'Office',
                   'soft_skills': 'Teamgeist', 'benefits': 'Weiterbildung'}
        created = self.client.post(create, payload)
        self.assertEqual(created.status_code, 302)
        new = Vacancy.objects.get(title='Neue Teststelle')
        self.assertFalse(new.published)
        self.assertEqual(self.client.get(reverse('hr_edit', args=['vacancy', new.pk])).status_code, 200)
        edit = reverse('hr_edit', args=['vacancy', self.vacancy.pk])
        self.assertEqual(self.client.get(edit).status_code, 200)
        self.assertEqual(self.client.get(reverse('translation_edit', args=['recruiting', 'vacancy', self.vacancy.pk])).status_code, 200)
        self.assertEqual(self.client.get(edit + '?step=review').status_code, 200)
