"""Publication and language-state regressions for machine variants."""
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission

from messen.models import MachineProduct, MachineVariant
from translations.models import ContentTranslation
from translations.services import fingerprint, translated


class MachinePublicationLanguageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="stage34_editor", password="test-only")
        self.user.user_permissions.add(Permission.objects.get(content_type__app_label="messen", codename="change_machinevariant"))
        self.client.force_login(self.user)
        self.product = MachineProduct.objects.create(category="vorbrecher", model_name="STAGE34", published=True)
        self.variant = MachineVariant.objects.create(product=self.product, name="STAGE34-A", description="Deutsch A", published=False)
        self.other = MachineVariant.objects.create(product=self.product, name="STAGE34-B", description="Deutsch B", published=True)
        self.url = reverse("staff_machine_variant_edit", args=[self.variant.pk])

    def add_translation(self, language, text, status="published"):
        return ContentTranslation.objects.create(
            content_type=ContentType.objects.get_for_model(self.variant),
            object_id=self.variant.pk, field_name="description", language=language,
            text=text, status=status, source_hash=fingerprint(self.variant.description),
            updated_by=self.user,
        )

    def payload(self, action="save", description="Deutsch neu", publish=False):
        data = {"editor_action": action, "product": str(self.product.pk),
                "name": self.variant.name, "description": description,
                "position": "0", "hero_media_choice": "auto"}
        if publish:
            data["published"] = "on"
        return data

    def test_draft_with_published_checkbox_does_not_publish(self):
        response = self.client.post(self.url, self.payload(action="draft", publish=True))
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertFalse(self.variant.published)
        self.assertEqual(self.variant.description, "Deutsch A")

    def test_regular_publication_does_not_change_other_variant(self):
        response = self.client.post(self.url, self.payload(publish=True))
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.other.refresh_from_db()
        self.assertTrue(self.variant.published)
        self.assertTrue(self.other.published)
        self.assertEqual(self.other.description, "Deutsch B")

    def test_german_edit_preserves_all_four_existing_language_records(self):
        entries = {lang: self.add_translation(lang, text) for lang, text in
                   (("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano"))}
        response = self.client.post(self.url, self.payload())
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.description, "Deutsch neu")
        for lang, entry in entries.items():
            entry.refresh_from_db()
            self.assertEqual(entry.text, {"en":"English","fr":"Français","es":"Español","it":"Italiano"}[lang])
            self.assertEqual(entry.status, "published")
            self.assertEqual(translated(self.variant, "description", lang), "Deutsch neu")

    def test_draft_translation_not_public_even_for_published_machine(self):
        self.variant.published = True
        self.variant.save(update_fields=["published"])
        entry = self.add_translation("en", "Unreviewed", status="draft")
        self.assertEqual(translated(self.variant, "description", "en"), "Deutsch A")
        entry.status = "published"
        entry.save(update_fields=["status"])
        self.assertEqual(translated(self.variant, "description", "en"), "Unreviewed")
