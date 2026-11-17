"""Regression checks for media isolation in machine variants (no file writes)."""
from django.test import TestCase
from messen.models import MachineProduct, MachineVariant, MachineVariantPhoto


class MachineVariantMediaTests(TestCase):
    def setUp(self):
        self.product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE303-PRODUCT", published=False
        )
        self.first = MachineVariant.objects.create(
            product=self.product, name="STAGE303-FIRST", published=False,
            image="machine-variants/first.jpg",
            technical_drawing="machine-variants/drawings/first.pdf",
            hero_video="machine-variants/videos/first.mp4",
        )
        self.second = MachineVariant.objects.create(
            product=self.product, name="STAGE303-SECOND", published=False,
            image="machine-variants/second.jpg",
            technical_drawing="machine-variants/drawings/second.pdf",
            hero_video="machine-variants/videos/second.mp4",
        )

    def photo(self, variant, name, position, cover=False):
        return MachineVariantPhoto.objects.create(
            variant=variant, image="machine-variants/gallery/" + name,
            position=position, is_cover=cover,
        )

    def test_media_fields_are_independent_for_each_variant(self):
        self.first.image = "machine-variants/updated.jpg"
        self.first.hero_video = "machine-variants/videos/updated.mp4"
        self.first.technical_drawing = "machine-variants/drawings/updated.pdf"
        self.first.save(update_fields=["image", "hero_video", "technical_drawing"])
        self.second.refresh_from_db()
        self.assertEqual(self.second.image.name, "machine-variants/second.jpg")
        self.assertEqual(self.second.hero_video.name, "machine-variants/videos/second.mp4")
        self.assertEqual(self.second.technical_drawing.name, "machine-variants/drawings/second.pdf")

    def test_gallery_order_is_scoped_to_variant(self):
        a = self.photo(self.first, "a.jpg", 0)
        b = self.photo(self.first, "b.jpg", 1)
        other = self.photo(self.second, "other.jpg", 0)
        MachineVariantPhoto.objects.filter(variant=self.first, pk=b.pk).update(position=0)
        MachineVariantPhoto.objects.filter(variant=self.first, pk=a.pk).update(position=1)
        other.refresh_from_db()
        self.assertEqual(other.position, 0)
        self.assertEqual(list(self.first.gallery.values_list("pk", flat=True)), [b.pk, a.pk])

    def test_cover_change_does_not_change_other_variant_cover(self):
        old = self.photo(self.first, "old.jpg", 0, cover=True)
        new = self.photo(self.first, "new.jpg", 1)
        other = self.photo(self.second, "other.jpg", 0, cover=True)
        self.first.gallery.update(is_cover=False)
        self.first.gallery.filter(pk=new.pk).update(is_cover=True)
        old.refresh_from_db()
        new.refresh_from_db()
        other.refresh_from_db()
        self.assertFalse(old.is_cover)
        self.assertTrue(new.is_cover)
        self.assertTrue(other.is_cover)

    def test_gallery_deletion_does_not_remove_other_variant_records(self):
        own = self.photo(self.first, "own.jpg", 0)
        other = self.photo(self.second, "other.jpg", 0)
        MachineVariantPhoto.objects.filter(variant=self.first, pk=own.pk).delete()
        self.assertFalse(MachineVariantPhoto.objects.filter(pk=own.pk).exists())
        self.assertTrue(MachineVariantPhoto.objects.filter(pk=other.pk).exists())

    def test_changing_media_urls_does_not_replace_uploaded_file_references(self):
        self.first.image_url = "https://example.org/new-photo.jpg"
        self.first.technical_drawing_url = "https://example.org/drawing.pdf"
        self.first.hero_video_url = "https://example.org/video.mp4"
        self.first.save(update_fields=["image_url", "technical_drawing_url", "hero_video_url"])
        self.first.refresh_from_db()
        self.assertEqual(self.first.image.name, "machine-variants/first.jpg")
        self.assertEqual(self.first.technical_drawing.name, "machine-variants/drawings/first.pdf")
        self.assertEqual(self.first.hero_video.name, "machine-variants/videos/first.mp4")
