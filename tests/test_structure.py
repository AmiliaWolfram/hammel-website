from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse, resolve


class ProjectStructureTests(SimpleTestCase):
    def test_home_route(self):
        self.assertEqual(reverse("home"), "/")

    def test_required_apps(self):
        for app in ("recruiting", "messen", "contacts", "partners"):
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_private_media_not_static(self):
        self.assertNotEqual(settings.MEDIA_ROOT, settings.STATIC_ROOT)
