"""Machine translations: preservation, visibility, and source freshness."""
import json
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from messen.models import MachineProduct, MachineVariant
from translations.models import ContentTranslation
from translations.services import fields_for, fingerprint, save_inline, translated


class MachineTranslationSafetyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage30_5", password="test-only"
        )
        self.product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE30-5",
            description="Deutsche Beschreibung", published=False
        )
        self.variant = MachineVariant.objects.create(
            product=self.product, name="STAGE30-5-D",
            description="Deutsche Variante", published=False
        )

    def translation(self, obj, language, text, status="published"):
        return ContentTranslation.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk, field_name="description", language=language,
            text=text, status=status,
            source_hash=fingerprint(obj.description), updated_by=self.user,
        )

    def test_product_and_variant_translations_are_independent(self):
        self.translation(self.product, "en", "Product description")
        self.translation(self.variant, "en", "Variant description")
        self.assertEqual(translated(self.product, "description", "en"), "Product description")
        self.assertEqual(translated(self.variant, "description", "en"), "Variant description")

    def test_original_edit_preserves_translation_record_and_marks_it_stale(self):
        entry = self.translation(self.variant, "fr", "Ancienne description")
        self.variant.description = "Neue deutsche Variante"
        self.variant.save(update_fields=["description"])
        entry.refresh_from_db()
        self.assertEqual(entry.text, "Ancienne description")
        self.assertEqual(entry.status, "published")
        self.assertEqual(translated(self.variant, "description", "fr"), "Neue deutsche Variante")

    def test_unpublished_translation_does_not_replace_german_original(self):
        self.translation(self.variant, "es", "Borrador", status="draft")
        self.assertEqual(translated(self.variant, "description", "es"), "Deutsche Variante")

    def test_missing_inline_payload_does_not_touch_existing_languages(self):
        entry = self.translation(self.variant, "it", "Descrizione italiana")
        request = SimpleNamespace(POST={}, user=self.user)
        save_inline(request, self.variant)
        entry.refresh_from_db()
        self.assertEqual(entry.text, "Descrizione italiana")
        self.assertEqual(entry.status, "published")

    def test_inline_edit_only_changes_explicitly_dirty_language(self):
        english = self.translation(self.variant, "en", "Old English")
        french = self.translation(self.variant, "fr", "Texte français")
        request = SimpleNamespace(
            POST={"inline_translations": json.dumps({
                "en": {"description": {
                    "dirty": True, "text": "New English", "status": "review"
                }},
                "fr": {"description": {
                    "dirty": False, "text": "Do not save", "status": "draft"
                }},
            })},
            user=self.user,
        )
        save_inline(request, self.variant)
        english.refresh_from_db()
        french.refresh_from_db()
        self.assertEqual((english.text, english.status), ("New English", "review"))
        self.assertEqual((french.text, french.status), ("Texte français", "published"))
        self.assertEqual(self.variant.description, "Deutsche Variante")

    def test_technical_identifiers_are_not_translatable(self):
        product_fields = {field.name for field in fields_for(self.product)}
        variant_fields = {field.name for field in fields_for(self.variant)}
        self.assertNotIn("model_name", product_fields)
        self.assertNotIn("engine", variant_fields)
        self.assertNotIn("weight", variant_fields)
        self.assertNotIn("image_url", variant_fields)
