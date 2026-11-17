"""End-to-end checks of recycling material scoping in machine editor."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from messen.models import (
    MachineProduct, MachineVariant, RecyclingArea, RecyclingMaterial,
    MachineVariantRevision,
)


class MachineMaterialEditorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stage36_materials", password="test-only"
        )
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="messen", codename="change_machinevariant"
        ))
        self.client.force_login(self.user)
        product = MachineProduct.objects.create(
            category="vorbrecher", model_name="STAGE36-PRODUCT", published=False
        )
        self.variant = MachineVariant.objects.create(
            product=product, name="STAGE36-VARIANT",
            description="Original", published=False,
        )
        self.other = MachineVariant.objects.create(
            product=product, name="STAGE36-OTHER", published=False
        )
        self.area_a = RecyclingArea.objects.create(slug="stage36-area-a", title="STAGE36 AREA A")
        self.area_b = RecyclingArea.objects.create(slug="stage36-area-b", title="STAGE36 AREA B")
        self.material_a = RecyclingMaterial.objects.create(
            area=self.area_a, name="STAGE36 Material A"
        )
        self.material_b = RecyclingMaterial.objects.create(
            area=self.area_b, name="STAGE36 Material B"
        )
        self.other.materials.add(self.material_b)
        self.url = reverse("staff_machine_variant_edit", args=[self.variant.pk])

    def payload(self):
        return {
            "editor_action": "save",
            "product": str(self.variant.product_id),
            "name": self.variant.name,
            "description": "Saved",
            "position": "0",
            "hero_media_choice": "auto",
        }

    def test_material_outside_selected_area_is_not_assigned(self):
        data = self.payload()
        data.update({"areas": [str(self.area_a.pk)],
                     "materials": [str(self.material_a.pk), str(self.material_b.pk)]})
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            set(self.variant.materials.values_list("pk", flat=True)),
            {self.material_a.pk},
        )
        self.assertEqual(
            set(self.other.materials.values_list("pk", flat=True)),
            {self.material_b.pk},
        )

    def test_invalid_save_does_not_create_new_material_or_revision(self):
        data = self.payload()
        data["name"] = ""
        data.update({"areas": [str(self.area_a.pk)],
                     "new_material_%s" % self.area_a.pk: "STAGE36 Not Created"})
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(RecyclingMaterial.objects.filter(
            area=self.area_a, name="STAGE36 Not Created"
        ).exists())
        self.assertFalse(MachineVariantRevision.objects.filter(
            variant=self.variant
        ).exists())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.description, "Original")

    def test_new_material_is_created_only_in_selected_area(self):
        data = self.payload()
        data.update({"areas": [str(self.area_a.pk)],
                     "new_material_%s" % self.area_a.pk: "STAGE36 New A",
                     "new_material_%s" % self.area_b.pk: "STAGE36 Ignore B"})
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        new_a = RecyclingMaterial.objects.get(
            area=self.area_a, name="STAGE36 New A"
        )
        self.assertTrue(self.variant.materials.filter(pk=new_a.pk).exists())
        self.assertFalse(RecyclingMaterial.objects.filter(
            area=self.area_b, name="STAGE36 Ignore B"
        ).exists())
