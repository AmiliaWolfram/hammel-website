"""Regression tests for variant-specific technical field isolation and visibility."""
from django.test import TestCase
from messen.models import (
    MachineProduct, MachineVariant, MachineField, MachineFieldSetting,
    MachineFieldValue,
)
from messen.staff_views import machine_field_visibility


class MachineVariantFieldTests(TestCase):
    def setUp(self):
        self.product = MachineProduct.objects.create(category="vorbrecher", model_name="STAGE30-2-A")
        self.other_product = MachineProduct.objects.create(category="vorbrecher", model_name="STAGE30-2-B")
        self.variant = MachineVariant.objects.create(product=self.product, name="STAGE30-2-A1")
        self.sibling = MachineVariant.objects.create(product=self.product, name="STAGE30-2-A2")
        self.other_variant = MachineVariant.objects.create(product=self.other_product, name="STAGE30-2-B1")
        self.field = MachineField.objects.create(key="stage30-2-spec", label="Testmerkmal")

    def test_custom_value_belongs_only_to_its_variant(self):
        MachineFieldValue.objects.create(field=self.field, variant=self.variant, text_value="100 kW")
        self.assertEqual(self.variant.custom_values.get(field=self.field).text_value, "100 kW")
        self.assertFalse(self.sibling.custom_values.filter(field=self.field).exists())
        self.assertFalse(self.other_variant.custom_values.filter(field=self.field).exists())

    def test_updating_variant_value_does_not_modify_other_variant(self):
        first = MachineFieldValue.objects.create(field=self.field, variant=self.variant, text_value="100 kW")
        second = MachineFieldValue.objects.create(field=self.field, variant=self.other_variant, text_value="200 kW")
        first.text_value = "120 kW"
        first.save(update_fields=["text_value"])
        second.refresh_from_db()
        self.assertEqual(second.text_value, "200 kW")

    def test_product_visibility_override_applies_only_to_its_product(self):
        MachineFieldSetting.objects.create(field=self.field, product=self.product, show_public=False)
        self.assertFalse(machine_field_visibility(self.field, self.variant))
        self.assertFalse(machine_field_visibility(self.field, self.sibling))
        self.assertTrue(machine_field_visibility(self.field, self.other_variant))

    def test_variant_override_takes_precedence_over_product_override(self):
        MachineFieldSetting.objects.create(field=self.field, product=self.product, show_public=False)
        MachineFieldSetting.objects.create(field=self.field, variant=self.variant, show_public=True)
        self.assertTrue(machine_field_visibility(self.field, self.variant))
        self.assertFalse(machine_field_visibility(self.field, self.sibling))

    def test_archived_field_is_hidden_even_with_variant_override(self):
        self.field.archived = True
        self.field.save(update_fields=["archived"])
        MachineFieldSetting.objects.create(field=self.field, variant=self.variant, show_public=True)
        self.assertFalse(machine_field_visibility(self.field, self.variant))
