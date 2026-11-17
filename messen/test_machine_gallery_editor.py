"""Regression tests for the extracted gallery editor operation."""
from types import SimpleNamespace

from django.http import QueryDict
from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from messen.models import MachineProduct, MachineVariant, MachineVariantPhoto
from messen.staff_views import save_machine_variant_gallery


class GalleryEditorIsolationTests(TestCase):
    def setUp(self):
        product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE306", published=False
        )
        self.first = MachineVariant.objects.create(
            product=product, name="STAGE306-A", published=False
        )
        self.second = MachineVariant.objects.create(
            product=product, name="STAGE306-B", published=False
        )

    def photo(self, variant, name, position=0, cover=False):
        return MachineVariantPhoto.objects.create(
            variant=variant, image="machine-variants/gallery/" + name,
            position=position, is_cover=cover,
        )

    def apply(self, variant, pairs=()):
        data = QueryDict(mutable=True)
        for key, value in pairs:
            data.appendlist(key, value)
        request = SimpleNamespace(POST=data, FILES=MultiValueDict())
        save_machine_variant_gallery(request, variant)

    def test_cross_variant_photo_deletion_is_ignored(self):
        own = self.photo(self.first, "own.jpg")
        foreign = self.photo(self.second, "foreign.jpg")
        self.apply(self.first, [("remove_photos", str(foreign.pk))])
        self.assertTrue(MachineVariantPhoto.objects.filter(pk=own.pk).exists())
        self.assertTrue(MachineVariantPhoto.objects.filter(pk=foreign.pk).exists())

    def test_order_updates_are_scoped_to_selected_variant(self):
        own = self.photo(self.first, "own.jpg", 5)
        foreign = self.photo(self.second, "foreign.jpg", 8)
        self.apply(self.first, [("gallery_order", f"{foreign.pk},{own.pk}")])
        own.refresh_from_db()
        foreign.refresh_from_db()
        self.assertEqual(own.position, 1)
        self.assertEqual(foreign.position, 8)

    def test_foreign_cover_id_cannot_select_foreign_photo(self):
        own = self.photo(self.first, "own.jpg", cover=True)
        foreign = self.photo(self.second, "foreign.jpg", cover=True)
        self.apply(self.first, [("cover_photo", str(foreign.pk))])
        own.refresh_from_db()
        foreign.refresh_from_db()
        self.assertTrue(own.is_cover)
        self.assertTrue(foreign.is_cover)

    def test_empty_request_preserves_existing_gallery(self):
        own = self.photo(self.first, "own.jpg", position=4, cover=True)
        self.apply(self.first)
        own.refresh_from_db()
        self.assertEqual(own.position, 4)
        self.assertTrue(own.is_cover)

    def test_unknown_cover_id_does_not_clear_current_cover(self):
        own = self.photo(self.first, "own.jpg", cover=True)
        self.apply(self.first, [("cover_photo", "999999999")])
        own.refresh_from_db()
        self.assertTrue(own.is_cover)

    def test_valid_cover_selection_changes_only_selected_variant(self):
        old = self.photo(self.first, "old.jpg", cover=True)
        new = self.photo(self.first, "new.jpg", cover=False)
        other = self.photo(self.second, "other.jpg", cover=True)
        self.apply(self.first, [("cover_photo", str(new.pk))])
        old.refresh_from_db()
        new.refresh_from_db()
        other.refresh_from_db()
        self.assertFalse(old.is_cover)
        self.assertTrue(new.is_cover)
        self.assertTrue(other.is_cover)
