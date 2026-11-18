import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from contacts.models import ContactGroup, ContactPerson


class ContactReorderTests(TestCase):
    def setUp(self):
        self.a = ContactGroup.objects.create(name="Test Group A", sort_order=10)
        self.b = ContactGroup.objects.create(name="Test Group B", sort_order=20)
        self.p = ContactPerson.objects.create(name="Test Person A", group=self.a)
        self.q = ContactPerson.objects.create(name="Test Person B", group=self.b)
        self.user = get_user_model().objects.create_user(
            username="contact_reorder_editor", password="test-only"
        )
        self.group_url = reverse("contacts_reorder", args=["gruppe"])
        self.person_url = reverse("contacts_reorder", args=["person"])

    def grant(self, codename):
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="contacts", codename=codename
        ))

    def post(self, url, ids):
        return self.client.post(url, data=json.dumps({"ids": ids}),
                                content_type="application/json")

    def test_anonymous_cannot_reorder(self):
        self.assertEqual(self.post(self.group_url, [self.b.pk, self.a.pk]).status_code, 302)
        self.a.refresh_from_db()
        self.assertEqual(self.a.sort_order, 10)

    def test_view_only_cannot_reorder(self):
        self.grant("view_contactgroup")
        self.client.force_login(self.user)
        self.assertEqual(self.post(self.group_url, [self.b.pk, self.a.pk]).status_code, 403)

    def test_group_reorder_updates_numbers(self):
        self.grant("change_contactgroup")
        self.client.force_login(self.user)
        ids = list(ContactGroup.objects.values_list("pk", flat=True))
        ids.remove(self.a.pk)
        ids.remove(self.b.pk)
        ids = [self.b.pk, self.a.pk] + ids
        self.assertEqual(self.post(self.group_url, ids).status_code, 200)
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual((self.b.sort_order, self.a.sort_order), (1, 2))

    def test_person_reorder_does_not_change_groups(self):
        self.grant("change_contactperson")
        self.client.force_login(self.user)
        ids = list(ContactPerson.objects.values_list("pk", flat=True))
        ids.remove(self.p.pk)
        ids.remove(self.q.pk)
        ids = [self.q.pk, self.p.pk] + ids
        self.assertEqual(self.post(self.person_url, ids).status_code, 200)
        self.p.refresh_from_db()
        self.q.refresh_from_db()
        self.assertEqual((self.q.sort_order, self.p.sort_order), (1, 2))
        self.a.refresh_from_db()
        self.assertEqual(self.a.sort_order, 10)

    def test_incomplete_order_rejected_without_changes(self):
        self.grant("change_contactgroup")
        self.client.force_login(self.user)
        self.assertEqual(self.post(self.group_url, [self.a.pk]).status_code, 409)
        self.a.refresh_from_db()
        self.assertEqual(self.a.sort_order, 10)

    def test_duplicate_ids_rejected(self):
        self.grant("change_contactgroup")
        self.client.force_login(self.user)
        self.assertEqual(self.post(self.group_url, [self.a.pk, self.a.pk]).status_code, 400)

    def test_get_not_allowed(self):
        self.grant("change_contactgroup")
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.group_url).status_code, 405)
