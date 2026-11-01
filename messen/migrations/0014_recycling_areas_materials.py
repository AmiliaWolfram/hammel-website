from django.db import migrations, models
import django.db.models.deletion

AREAS = [
 ("schrott","Schrottverarbeitung",["Mischschrott","Aluminium","Metallschrott"]),
 ("holz","Altholz & Grünabfälle",["Altholz","Bau- & Abbruchholz","Wurzelstöcke","Grünschnitt","Paletten","Holzkabeltrommeln"]),
 ("muell","Gewerbe-, Industrie- & Hausmüll",["Hausmüll","Industriemüll","Gewerbemüll"]),
 ("bauschutt","Bauschutt",["Baustellenabfälle","Mineralische Materialien"]),
 ("kunststoff","Gummi-/Kunststoff & Kunststoffabfälle",["Kunststoffe","Gummiabfälle"]),
]
def seed_areas(apps,schema_editor):
    Area=apps.get_model("messen","RecyclingArea")
    Material=apps.get_model("messen","RecyclingMaterial")
    Variant=apps.get_model("messen","MachineVariant")
    from django.db import IntegrityError
    for i,(slug,title,materials) in enumerate(AREAS):
        a,_=Area.objects.get_or_create(slug=slug,defaults={"title":title,"position":i})
        for j,name in enumerate(materials):
            Material.objects.get_or_create(area=a,name=name,defaults={"position":j})
    # Carry forward the existing per-variant wood/waste descriptions.
    for v in Variant.objects.all():
        for slug,text in [("holz",v.applications_wood),("muell",v.applications_waste)]:
            if not text:continue
            a=Area.objects.get(slug=slug)
            for part in text.replace("\\n",",").split(","):
                label=part.strip()
                if not label:continue
                if label=="Kabeltrommeln":label="Holzkabeltrommeln"
                if label=="Industrie- & Gewerbemüll":
                    labels=["Industriemüll","Gewerbemüll"]
                else:labels=[label]
                for name in labels:
                    m,_=Material.objects.get_or_create(area=a,name=name)
                    v.materials.add(m)
        # Other legacy values remain in applications_other for manual classification.

class Migration(migrations.Migration):
    dependencies=[("messen","0013_vertrieb_machine_variant_permissions")]
    operations=[
      migrations.CreateModel(name="RecyclingArea",fields=[
        ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
        ("slug",models.SlugField(unique=True)),("title",models.CharField(max_length=180)),
        ("position",models.PositiveSmallIntegerField(default=0))],
        options={"ordering":("position","pk"),"verbose_name":"Recyclingbereich","verbose_name_plural":"Recyclingbereiche"}),
      migrations.CreateModel(name="RecyclingMaterial",fields=[
        ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
        ("name",models.CharField(max_length=180)),("position",models.PositiveSmallIntegerField(default=0)),
        ("area",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="materials",to="messen.recyclingarea"))],
        options={"ordering":("position","pk")}),
      migrations.AddConstraint(model_name="recyclingmaterial",constraint=models.UniqueConstraint(fields=("area","name"),name="unique_recycling_material_per_area")),
      migrations.AddField(model_name="machinevariant",name="materials",field=models.ManyToManyField(blank=True,related_name="machine_variants",to="messen.recyclingmaterial",verbose_name="Einsatzmaterialien")),
      migrations.RunPython(seed_areas,migrations.RunPython.noop),
    ]
