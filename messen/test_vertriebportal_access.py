"""Regression tests for sales-portal access without changing UI or records."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class VertriebportalAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="sales_stage29", password="test-only-password"
        )
        self.url = reverse("staff_machine_dashboard")

    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_without_sales_permission_is_denied(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_product_view_permission_allows_dashboard(self):
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="messen",
                codename="view_machineproduct",
            )
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_add_product"])
        self.assertFalse(response.context["can_add_variant"])

    def test_variant_view_permission_allows_dashboard(self):
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="messen",
                codename="view_machinevariant",
            )
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_add_product"])
        self.assertFalse(response.context["can_add_variant"])

    def test_add_permissions_are_reflected_in_dashboard_context(self):
        permissions = Permission.objects.filter(
            content_type__app_label="messen",
            codename__in=[
                "view_machineproduct",
                "add_machineproduct",
                "add_machinevariant",
            ],
        )
        self.user.user_permissions.add(*permissions)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["can_add_product"])
        self.assertTrue(response.context["can_add_variant"])
