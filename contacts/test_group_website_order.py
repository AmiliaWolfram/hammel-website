import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from contacts.models import ContactGroup, ContactPerson

class GroupWebsiteOrderTests(TestCase):
    def setUp(self):
        self.a=ContactGroup.objects.create(name="Order Group A",sort_order=200)
        self.b=ContactGroup.objects.create(name="Order Group B",sort_order=201)
        self.p=ContactPerson.objects.create(name="Order Person A",group=self.a,sort_order=20)
        self.q=ContactPerson.objects.create(name="Order Person B",group=self.a,sort_order=30)
        self.other=ContactPerson.objects.create(name="Order Person Other",group=self.b,sort_order=7)
        self.url=reverse("contacts_group_people_reorder",args=[self.a.pk])
        self.user=get_user_model().objects.create_user(username="group_order_editor",password="test-only")
    def post(self,ids):return self.client.post(self.url,data=json.dumps({"ids":ids}),content_type="application/json")
    def test_anonymous_cannot_reorder(self):
        self.assertEqual(self.post([self.q.pk,self.p.pk]).status_code,302)
    def test_view_permission_cannot_reorder(self):
        self.user.user_permissions.add(Permission.objects.get(content_type__app_label="contacts",codename="view_contactperson"))
        self.client.force_login(self.user)
        self.assertEqual(self.post([self.q.pk,self.p.pk]).status_code,403)
    def test_group_reorder_keeps_other_groups_intact(self):
        self.user.user_permissions.add(Permission.objects.get(content_type__app_label="contacts",codename="change_contactperson"))
        self.client.force_login(self.user)
        self.assertEqual(self.post([self.q.pk,self.p.pk]).status_code,200)
        self.p.refresh_from_db();self.q.refresh_from_db();self.other.refresh_from_db()
        self.assertEqual((self.q.sort_order,self.p.sort_order,self.other.sort_order),(1,2,7))
    def test_foreign_contact_rejected(self):
        self.user.user_permissions.add(Permission.objects.get(content_type__app_label="contacts",codename="change_contactperson"))
        self.client.force_login(self.user)
        self.assertEqual(self.post([self.q.pk,self.other.pk]).status_code,409)
        self.p.refresh_from_db();self.assertEqual(self.p.sort_order,20)
    def test_missing_contact_rejected(self):
        self.user.user_permissions.add(Permission.objects.get(content_type__app_label="contacts",codename="change_contactperson"))
        self.client.force_login(self.user)
        self.assertEqual(self.post([self.p.pk]).status_code,409)
