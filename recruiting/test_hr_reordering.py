"""HRPortal drag-and-drop tests. Run: python manage.py test recruiting.test_hr_reordering"""
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from recruiting.models import HRTip, ApplicationDepartment


class HRReorderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="hr_reorder_test", password="test-only-password"
        )
        cls.tip_a = HRTip.objects.create(title="A", body="A", order=1)
        cls.tip_b = HRTip.objects.create(title="B", body="B", order=2)
        cls.dep_a = ApplicationDepartment.objects.create(name="Test A", sort_order=1)
        cls.dep_b = ApplicationDepartment.objects.create(name="Test B", sort_order=2)

    @staticmethod
    def complete_ids(model, order_field, first, second):
        """Include records installed by initial-data migrations or fixtures."""
        all_ids = list(model.objects.order_by(order_field, "pk").values_list("pk", flat=True))
        return [second, first] + [pk for pk in all_ids if pk not in (first, second)]

    def post_order(self, route, ids, raw=False):
        body = ids if raw else json.dumps(ids)
        return self.client.post(
            reverse(route), data=body, content_type="application/json"
        )

    def login_with_permissions(self, *codenames):
        self.user.user_permissions.add(
            *Permission.objects.filter(
                content_type__app_label="recruiting", codename__in=codenames
            )
        )
        self.client.force_login(self.user)

    def test_tips_reorder_persists_and_preserves_fields(self):
        self.login_with_permissions("change_hrtip")
        ids = self.complete_ids(HRTip, "order", self.tip_a.pk, self.tip_b.pk)
        response = self.post_order("hr_reorder_tips", ids)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ids"], ids)
        self.assertEqual(
            list(HRTip.objects.order_by("order").values_list("pk", flat=True)), ids
        )
        self.tip_a.refresh_from_db()
        self.assertEqual(self.tip_a.title, "A")
        self.assertTrue(self.tip_a.published)

    def test_departments_reorder_persists_and_preserves_active(self):
        self.login_with_permissions("change_applicationdepartment")
        ids = self.complete_ids(ApplicationDepartment, "sort_order", self.dep_a.pk, self.dep_b.pk)
        response = self.post_order("hr_reorder_departments", ids)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(ApplicationDepartment.objects.order_by("sort_order").values_list("pk", flat=True)),
            ids,
        )
        self.dep_a.refresh_from_db()
        self.assertTrue(self.dep_a.active)

    def test_invalid_json_is_rejected_without_changes(self):
        self.login_with_permissions("change_hrtip")
        response = self.post_order("hr_reorder_tips", "{broken", raw=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.tip_a.order, HRTip.objects.get(pk=self.tip_a.pk).order)

    def test_duplicates_and_wrong_types_are_rejected(self):
        self.login_with_permissions("change_hrtip")
        for ids in ([self.tip_a.pk, self.tip_a.pk], [True, self.tip_b.pk], ["1", 2]):
            with self.subTest(ids=ids):
                self.assertEqual(self.post_order("hr_reorder_tips", ids).status_code, 400)

    def test_stale_list_returns_conflict_without_partial_updates(self):
        self.login_with_permissions("change_hrtip")
        response = self.post_order("hr_reorder_tips", [self.tip_a.pk])
        self.assertEqual(response.status_code, 409)
        self.assertEqual(HRTip.objects.get(pk=self.tip_a.pk).order, 1)
        self.assertEqual(HRTip.objects.get(pk=self.tip_b.pk).order, 2)

    def test_departments_reject_empty_list(self):
        self.login_with_permissions("change_applicationdepartment")
        self.assertEqual(self.post_order("hr_reorder_departments", []).status_code, 400)

    def test_unauthorized_user_cannot_reorder(self):
        self.client.force_login(self.user)
        response = self.post_order("hr_reorder_tips", [self.tip_b.pk, self.tip_a.pk])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(HRTip.objects.get(pk=self.tip_a.pk).order, 1)

    def test_database_error_rolls_back_first_update(self):
        self.login_with_permissions("change_hrtip")
        original_order = dict(HRTip.objects.values_list("pk", "order"))
        ids = self.complete_ids(HRTip, "order", self.tip_a.pk, self.tip_b.pk)
        original_filter = HRTip.objects.filter
        calls = {"count": 0}

        def wrapped_filter(*args, **kwargs):
            calls["count"] += 1
            if calls["count"] == 2:
                raise RuntimeError("Simulated database failure")
            return original_filter(*args, **kwargs)

        with patch.object(HRTip.objects, "filter", side_effect=wrapped_filter):
            with self.assertRaises(RuntimeError):
                self.post_order("hr_reorder_tips", ids)
        self.assertEqual(dict(HRTip.objects.values_list("pk", "order")), original_order)
