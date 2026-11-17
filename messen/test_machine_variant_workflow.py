"""Regression tests for draft, preview, and revision workflows in Vertriebportal."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from messen.models import (
    MachineProduct, MachineVariant, MachineVariantDraft, MachineVariantRevision
)


class MachineVariantWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage30_variant_workflow", password="test-only"
        )
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="messen",
            codename="change_machinevariant",
        ))
        self.client.force_login(self.user)
        product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE30-4-PRODUCT", published=False
        )
        self.first = MachineVariant.objects.create(
            product=product, name="STAGE30-4-A", description="Original A",
            published=False,
        )
        self.second = MachineVariant.objects.create(
            product=product, name="STAGE30-4-B", description="Original B",
            published=True,
        )
        self.url = reverse("staff_machine_variant_edit", args=[self.first.pk])

    def payload(self, action, description="New description"):
        return {
            "editor_action": action,
            "product": str(self.first.product_id),
            "name": self.first.name,
            "description": description,
            "position": "0",
            "hero_media_choice": "auto",
        }

    def test_draft_does_not_change_live_variant_or_publication(self):
        response = self.client.post(self.url, self.payload("draft"))
        self.assertEqual(response.status_code, 302)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Original A")
        self.assertFalse(self.first.published)
        draft = MachineVariantDraft.objects.get(variant=self.first)
        self.assertEqual(draft.values["description"], "New description")
        self.assertEqual(draft.author, self.user)

    def test_repeated_draft_updates_one_draft_instead_of_duplicating(self):
        self.client.post(self.url, self.payload("draft", "First"))
        self.client.post(self.url, self.payload("draft", "Second"))
        self.assertEqual(
            MachineVariantDraft.objects.filter(variant=self.first).count(), 1
        )
        self.assertEqual(
            MachineVariantDraft.objects.get(variant=self.first).values["description"],
            "Second",
        )

    def test_draft_is_isolated_from_other_variants(self):
        self.client.post(self.url, self.payload("draft"))
        self.second.refresh_from_db()
        self.assertEqual(self.second.description, "Original B")
        self.assertTrue(self.second.published)
        self.assertFalse(
            MachineVariantDraft.objects.filter(variant=self.second).exists()
        )

    def test_preview_does_not_save_variant_or_revision(self):
        from messen.forms import MachineVariantForm
        payload = self.payload("preview")
        self.assertTrue(MachineVariantForm(payload, instance=self.first).is_valid())
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Original A")
        self.assertFalse(
            MachineVariantRevision.objects.filter(variant=self.first).exists()
        )

    def test_regular_save_creates_revision_and_removes_draft(self):
        self.client.post(self.url, self.payload("draft", "Temporary"))
        from messen.forms import MachineVariantForm
        payload = self.payload("save", "Saved")
        self.assertTrue(MachineVariantForm(payload, instance=self.first).is_valid())
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 302)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Saved")
        self.assertFalse(
            MachineVariantDraft.objects.filter(variant=self.first).exists()
        )
        revision = MachineVariantRevision.objects.get(variant=self.first)
        self.assertEqual(revision.author, self.user)
        self.assertEqual(revision.action, "saved")
        self.assertEqual(revision.snapshot["description"], "Original A")

    def test_invalid_variant_form_renders_errors_without_server_exception(self):
        payload = self.payload("save", "Must not be saved")
        payload["name"] = ""
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name=\"name\"", status_code=200)
        self.assertTrue(response.context["form"].errors)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Original A")
        self.assertFalse(
            MachineVariantRevision.objects.filter(variant=self.first).exists()
        )

    def test_invalid_preview_does_not_write_variant_revision_or_draft(self):
        payload = self.payload("preview", "Preview must not persist")
        payload["name"] = ""
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Original A")
        self.assertFalse(self.first.published)
        self.assertFalse(MachineVariantRevision.objects.filter(variant=self.first).exists())
        self.assertFalse(MachineVariantDraft.objects.filter(variant=self.first).exists())

    def test_invalid_final_save_keeps_existing_draft_and_live_values(self):
        draft_payload = self.payload("draft", "Work in progress")
        self.assertEqual(self.client.post(self.url, draft_payload).status_code, 302)
        payload = self.payload("save", "Invalid final")
        payload["name"] = ""
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.first.refresh_from_db()
        self.assertEqual(self.first.description, "Original A")
        self.assertEqual(
            MachineVariantDraft.objects.get(variant=self.first).values["description"],
            "Work in progress",
        )
        self.assertFalse(MachineVariantRevision.objects.filter(variant=self.first).exists())
