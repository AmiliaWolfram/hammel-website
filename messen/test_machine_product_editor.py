"""Regression tests for machine product creation and editing in Vertriebportal."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from messen.models import MachineProduct


class MachineProductEditorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage30_product_editor", password="test-only"
        )
        self.client.force_login(self.user)
        self.other = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE30-OTHER",
            description="Unverändert", published=False
        )
        self.create_url = reverse("staff_machine_product_create")
        self.edit_url = reverse("staff_machine_product_edit", args=[self.other.pk])

    def grant(self, codename):
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="messen", codename=codename
        ))

    def payload(self, model_name="STAGE30-NEW", description="Beschreibung"):
        return {
            "category": "vorbrecher", "model_name": model_name,
            "headline": "Kurzbeschreibung", "description": description,
            "advantages": "Vorteil", "image_url": "", "position": "3",
        }

    def test_create_requires_add_permission(self):
        response = self.client.post(self.create_url, self.payload())
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MachineProduct.objects.filter(model_name="STAGE30-NEW").exists())

    def test_edit_requires_change_permission(self):
        response = self.client.post(
            self.edit_url, self.payload("STAGE30-OTHER", "Geändert")
        )
        self.assertEqual(response.status_code, 403)
        self.other.refresh_from_db()
        self.assertEqual(self.other.description, "Unverändert")

    def test_create_saves_one_product_without_changing_existing(self):
        self.grant("add_machineproduct")
        response = self.client.post(self.create_url, self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            MachineProduct.objects.filter(model_name="STAGE30-NEW").count(), 1
        )
        self.other.refresh_from_db()
        self.assertEqual(self.other.description, "Unverändert")

    def test_edit_updates_only_selected_product(self):
        self.grant("change_machineproduct")
        second = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE30-SECOND",
            description="Bleibt", published=False
        )
        response = self.client.post(
            self.edit_url, self.payload("STAGE30-OTHER", "Neue Beschreibung")
        )
        self.assertEqual(response.status_code, 302)
        self.other.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(self.other.description, "Neue Beschreibung")
        self.assertEqual(second.description, "Bleibt")

    def test_repeated_create_does_not_duplicate_unique_model_name(self):
        self.grant("add_machineproduct")
        first = self.client.post(self.create_url, self.payload())
        second = self.client.post(self.create_url, self.payload())
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            MachineProduct.objects.filter(model_name="STAGE30-NEW").count(), 1
        )

    def test_invalid_edit_does_not_overwrite_existing_values(self):
        self.grant("change_machineproduct")
        invalid = self.payload("", "Should not save")
        response = self.client.post(self.edit_url, invalid)
        self.assertEqual(response.status_code, 200)
        self.other.refresh_from_db()
        self.assertEqual(self.other.description, "Unverändert")
