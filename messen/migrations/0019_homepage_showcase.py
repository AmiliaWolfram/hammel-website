from django.db import migrations, models
import django.db.models.deletion

INITIAL = [{'button_text': 'VORBRECHER ENTDECKEN',
  'button_url': 'https://www.hammel.de/index.php/de/produkte/vorbrecher',
  'category': 'Vorbrecher',
  'is_default': True,
  'description': 'Leistungsstarke Vorzerkleinerung',
  'eyebrow': 'RED GIANT',
  'headline': 'VB 950 DK',
  'image_path': 'assets/img/machines/vb950.webp',
  'other_models': 'VB 850 DK · VB 750 DLV · VB 650 · VB 450',
  'position': 0},
 {'button_text': 'NACHZERKLEINERER ENTDECKEN',
  'button_url': 'https://www.hammel.de/index.php/de/produkte/nachzerkleinerer',
  'category': 'Nachzerkleinerer',
  'is_default': False,
  'description': 'Für ein gleichmäßiges Endprodukt',
  'eyebrow': 'PRÄZISE NACHZERKLEINERUNG',
  'headline': 'NZS 1000 DK',
  'image_path': 'https://www.hammel.de/images/revslider/uploads/Nachzerkleinerer/1000/NZS%201000%20DK.png',
  'other_models': 'NZS 700 · HEM 400 D · HEM 1250',
  'position': 10},
 {'button_text': 'SIEBTECHNIK ENTDECKEN',
  'button_url': 'https://www.hammel.de/index.php/de/produkte/siebtechnik',
  'category': 'Siebtechnik',
  'is_default': False,
  'description': 'Drei Fraktionen in einem Arbeitsgang',
  'eyebrow': 'EFFIZIENTE SIEBUNG',
  'headline': 'HZ 52 DT',
  'image_path': '',
  'other_models': 'HZ 16',
  'position': 20},
 {'button_text': 'SORTIERTECHNIK ENTDECKEN',
  'button_url': 'https://www.hammel.de/index.php/de/produkte/sortiertechnik',
  'category': 'Sortiertechnik',
  'is_default': False,
  'description': 'Sortiertechnik für die Aufbereitung von Wertstoffen',
  'eyebrow': 'PRÄZISE SORTIERUNG',
  'headline': 'MSS 1000 E',
  'image_path': 'assets/img/machines/mss1000e.webp',
  'other_models': 'MMA 1400 E · MWA 1000 E · MMS 150 DK · SMA',
  'position': 30},
 {'button_text': 'ANLAGENBAU ENTDECKEN',
  'button_url': 'https://www.hammel.de/index.php/de/produkte/anlagebau',
  'category': 'Anlagenbau',
  'is_default': False,
  'description': 'Integrierte Lösungen für Recyclingprozesse',
  'eyebrow': 'INDIVIDUELLE SYSTEME',
  'headline': 'HAMMEL ANLAGENBAU',
  'image_path': 'assets/img/machines/metallanlage.webp',
  'other_models': 'Planung · Kombination · Integration',
  'position': 40}]

def seed(apps, schema_editor):
    Showcase = apps.get_model('messen','HomepageShowcase')
    for item in INITIAL:
        Showcase.objects.get_or_create(category=item['category'], defaults=item)

class Migration(migrations.Migration):
    dependencies = [('messen','0018_editor_workflow')]
    operations = [
        migrations.CreateModel(name='HomepageShowcase',fields=[
            ('id',models.BigAutoField(primary_key=True,serialize=False)),
            ('category',models.CharField(max_length=80,unique=True,verbose_name='Kategorie')),
            ('eyebrow',models.CharField(blank=True,max_length=120,verbose_name='Oberzeile')),
            ('headline',models.CharField(max_length=160,verbose_name='Titel')),
            ('description',models.CharField(blank=True,max_length=300,verbose_name='Werbetext')),
            ('other_models',models.CharField(blank=True,max_length=300,verbose_name='Weitere Modelle')),
            ('image',models.ImageField(blank=True,upload_to='homepage-showcase/',verbose_name='Eigenes Bild')),
            ('image_path',models.CharField(blank=True,max_length=300,verbose_name='Vorhandenes Bild (Pfad)')),
            ('button_text',models.CharField(blank=True,max_length=120,verbose_name='Button-Text')),
            ('button_url',models.CharField(blank=True,max_length=400,verbose_name='Button-Link')),
            ('position',models.PositiveIntegerField(default=0,verbose_name='Reihenfolge')),
            ('is_default',models.BooleanField(default=False,verbose_name='Beim Laden zuerst anzeigen')),
            ('published',models.BooleanField(default=True,verbose_name='Sichtbar')),
            ('product',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='homepage_showcases',to='messen.machineproduct'))
        ],options={'ordering':['position','pk']}),
        migrations.RunPython(seed,migrations.RunPython.noop),
    ]
