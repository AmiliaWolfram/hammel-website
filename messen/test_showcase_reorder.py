import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from messen.models import HomepageShowcase


class ShowcaseReorderTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="showcase_sort_test", password="test")
        self.url = reverse("showcase_reorder")
        self.ids = list(HomepageShowcase.objects.values_list("pk", flat=True))

    def grant(self):
        self.user.user_permissions.add(Permission.objects.get(
            content_type__app_label="messen", codename="change_homepageshowcase"
        ))

    def post(self, ids):
        return self.client.post(self.url, json.dumps({"ids": ids}), content_type="application/json")

    def test_anonymous_cannot_change_order(self):
        self.assertEqual(self.post(self.ids).status_code, 302)

    def test_user_without_change_permission_cannot_reorder(self):
        self.client.force_login(self.user)
        self.assertEqual(self.post(self.ids).status_code, 403)

    def test_duplicate_ids_rejected(self):
        self.grant()
        self.client.force_login(self.user)
        self.assertEqual(self.post([1, 1]).status_code, 400)

    def test_incomplete_list_rejected_if_records_exist(self):
        if not self.ids:
            self.skipTest("No showcase fixtures")
        self.grant()
        self.client.force_login(self.user)
        self.assertEqual(self.post([]).status_code, 409)

    def test_reorder_persists_positions_without_changing_other_fields(self):
        if len(self.ids) < 2:
            self.skipTest("At least two showcase entries required")
        self.grant()
        self.client.force_login(self.user)
        ids=list(reversed(self.ids))
        original=dict(
            (pk, (headline, published))
            for pk, headline, published in HomepageShowcase.objects.values_list(
                "pk", "headline", "published"
            )
        )
        self.assertEqual(self.post(ids).status_code, 200)
        for i,pk in enumerate(ids,1):
            self.assertEqual(HomepageShowcase.objects.get(pk=pk).position,i)
        after = dict(
            (pk, (headline, published))
            for pk, headline, published in HomepageShowcase.objects.values_list(
                "pk", "headline", "published"
            )
        )
        self.assertEqual(original, after)

    def test_get_not_allowed(self):
        self.grant()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)
