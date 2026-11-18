from django.test import TestCase
from messen.models import RecyclingArea, RecyclingMaterial

class FourRecyclingAreasTests(TestCase):
    def test_default_categories_in_requested_order(self):
        self.assertEqual(
            list(RecyclingArea.objects.order_by('position').values_list('slug', 'title')),
            [('holz', 'Altholz & Grünabfälle'),
             ('muell', 'Gewerbe-, Industrie- & Hausmüll'),
             ('schrott', 'Metallrecycling'),
             ('spezial', 'Spezial Anwendung')]
        )
    def test_special_area_contains_legacy_materials(self):
        special = RecyclingArea.objects.get(slug='spezial')
        self.assertTrue(RecyclingMaterial.objects.filter(area=special, name='Baustellenabfälle').exists())
        self.assertTrue(RecyclingMaterial.objects.filter(area=special, name='Kunststoffe').exists())
