"""Security regression tests for Vertriebportal editing, drafts and publication."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from messen.models import MachineProduct, MachineVariant, MachineVariantDraft, MachineVariantRevision


class VertriebportalPermissionDraftTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage33_editor", password="test-only"
        )
        self.product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE33-PRODUCT", published=False
        )
        self.variant = MachineVariant.objects.create(
            product=self.product, name="STAGE33-A",
            description="Original", published=False,
        )
        self.edit_url = reverse("staff_machine_variant_edit", args=[self.variant.pk])
        self.create_url = reverse("staff_machine_variant_create")
        self.payload = {
            "editor_action": "save",
            "product": str(self.product.pk),
            "name": self.variant.name,
            "description": "Changed",
            "position": "0",
            "hero_media_choice": "auto",
            "published": "on",
        }

    def grant(self, codename):
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="messen", codename=codename
        ))

    def test_anonymous_editor_post_redirects_without_changes(self):
        response = self.client.post(self.edit_url, self.payload)
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.description, "Original")
        self.assertFalse(self.variant.published)
        self.assertFalse(MachineVariantRevision.objects.filter(variant=self.variant).exists())

    def test_view_only_user_cannot_publish_or_edit_variant(self):
        self.grant("view_machinevariant")
        self.client.force_login(self.user)
        response = self.client.post(self.edit_url, self.payload)
        self.assertEqual(response.status_code, 403)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.description, "Original")
        self.assertFalse(self.variant.published)
        self.assertFalse(MachineVariantRevision.objects.filter(variant=self.variant).exists())

    def test_add_permission_does_not_grant_change_permission(self):
        self.grant("add_machinevariant")
        self.client.force_login(self.user)
        response = self.client.post(self.edit_url, self.payload)
        self.assertEqual(response.status_code, 403)
        self.variant.refresh_from_db()
        self.assertFalse(self.variant.published)

    def test_change_permission_does_not_grant_create_permission(self):
        self.grant("change_machinevariant")
        self.client.force_login(self.user)
        response = self.client.post(self.create_url, self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MachineVariant.objects.filter(name="STAGE33-A").count(), 1)

    def test_view_only_user_cannot_save_draft(self):
        self.grant("view_machinevariant")
        self.client.force_login(self.user)
        payload = dict(self.payload, editor_action="draft")
        response = self.client.post(self.edit_url, payload)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MachineVariantDraft.objects.filter(variant=self.variant).exists())

    def test_authorized_draft_does_not_publish_live_variant(self):
        self.grant("change_machinevariant")
        self.client.force_login(self.user)
        payload = dict(self.payload, editor_action="draft")
        response = self.client.post(self.edit_url, payload)
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.description, "Original")
        self.assertFalse(self.variant.published)
        self.assertTrue(MachineVariantDraft.objects.filter(variant=self.variant).exists())
        self.assertFalse(MachineVariantRevision.objects.filter(variant=self.variant).exists())
