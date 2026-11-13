from django.test import SimpleTestCase
from django.urls import reverse

class NewsLanguageRoutesTests(SimpleTestCase):
    def test_language_routes(self):
        self.assertEqual(reverse("news_language_editor", args=[12, "en"]), "/staff/news/12/sprache/en/")
        self.assertEqual(reverse("news_language_editor", args=[12, "review"]), "/staff/news/12/sprache/review/")
