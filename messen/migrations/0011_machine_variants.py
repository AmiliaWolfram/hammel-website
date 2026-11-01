from django.db import migrations, models
import django.db.models.deletion

def seed(apps, schema_editor):
    Product = apps.get_model("messen", "MachineProduct")
    Variant = apps.get_model("messen", "MachineVariant")
    p = Product.objects.filter(model_name="VB 450").first()
    if not p: return
    common = dict(applications_wood="Altholz, Bau- & Abbruchholz, Wurzelstöcke, Grünschnitt, Paletten, Kabeltrommeln", applications_waste="Hausmüll, Industrie- & Gewerbemüll", operating_principle="Hydraulisch arbeitende Recyclingmaschine mit 2 langsam laufenden Werkzeugwellen")
    for pos,name,version,engine,drive,weight in [
      (0,"VB 450 D","Hakenlift","Cummins F3.8 - Stage 5","145 PS","8 t Maschine + 1 t Magnet"),
      (1,"VB 450 DK","Kette","Cummins F3.8 - Stage 5","145 PS","9 t Maschine + 1 t Magnet"),
      (2,"VB 450 E","Elektrisch","-","110 kW","8 t Maschine + 1 t Magnet")]:
        Variant.objects.get_or_create(name=name, defaults=dict(product=p, version=version, engine=engine, drive=drive, weight=weight, position=pos, published=True, **common))
    # Other series are not seeded with guessed specifications. Vertrieb can add verified variants.
    Group=apps.get_model("auth","Group")
    Permission=apps.get_model("auth","Permission")
    group,_=Group.objects.get_or_create(name="Vertrieb")
    group.permissions.add(*Permission.objects.filter(content_type__app_label="messen",content_type__model="machinevariant"))

class Migration(migrations.Migration):
    dependencies = [("messen","0010_machine_catalog"),("auth","0012_alter_user_first_name_max_length")]
    operations = [
      migrations.CreateModel(name="MachineVariant", fields=[
        ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
        ("name",models.CharField(max_length=130,unique=True,verbose_name="Modellversion")),
        ("version",models.CharField(max_length=120,blank=True,verbose_name="Ausführung")),
        ("engine",models.CharField(max_length=240,blank=True,verbose_name="Motor")),
        ("drive",models.CharField(max_length=140,blank=True,verbose_name="Antrieb / Leistung")),
        ("weight",models.CharField(max_length=180,blank=True,verbose_name="Gewicht")),
        ("applications_wood",models.TextField(blank=True,verbose_name="Einsatzgebiet Holz")),
        ("applications_waste",models.TextField(blank=True,verbose_name="Einsatzgebiet Müll")),
        ("applications_other",models.TextField(blank=True,verbose_name="Weitere Einsatzgebiete")),
        ("operating_principle",models.TextField(blank=True,verbose_name="Funktionsprinzip")),
        ("description",models.TextField(blank=True,verbose_name="Beschreibung")),
        ("additional_specs",models.TextField(blank=True,verbose_name="Weitere technische Daten (eine Zeile: Merkmal: Wert)")),
        ("image",models.ImageField(blank=True,upload_to="machine-variants/",verbose_name="Maschinenfoto")),
        ("image_url",models.URLField(blank=True,verbose_name="Foto-URL")),
        ("datasheet_url",models.URLField(blank=True,verbose_name="Datenblatt")),
        ("published",models.BooleanField(default=False,verbose_name="Veröffentlicht")),
        ("position",models.PositiveIntegerField(default=0,verbose_name="Reihenfolge")),
        ("product",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="variants",to="messen.machineproduct",verbose_name="Baureihe")),
      ],options={"ordering":["position","name"],"verbose_name":"Maschinenvariante","verbose_name_plural":"Maschinenvarianten"}),
      migrations.RunPython(seed,migrations.RunPython.noop),
    ]
