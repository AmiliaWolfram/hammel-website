from django.db import migrations, models
import django.db.models.deletion

SYSTEM = [("version","Ausführung","general"),("description","Beschreibung","general"),("operating_principle","Funktionsprinzip","general"),("engine","Motor","technical"),("drive","Antrieb / Leistung","technical"),("weight","Gewicht","technical"),("additional_specs","Weitere technische Daten","technical"),("materials","Einsatzgebiete","applications"),("image","Maschinenfoto","media"),("hero_video","Hero-Video","media"),("datasheet_url","Datenblatt","media"),("technical_drawing","Technische Zeichnung","media")]
def seed(apps,schema_editor):
    Field=apps.get_model("messen","MachineField")
    for pos,(key,label,section) in enumerate(SYSTEM):
        Field.objects.get_or_create(key=key,defaults={"label":label,"section":section,"position":pos,"is_system":True})
class Migration(migrations.Migration):
    dependencies=[("messen","0016_variant_technical_drawing")]
    operations=[
      migrations.CreateModel(name="MachineField",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("key",models.SlugField(max_length=100,unique=True)),("label",models.CharField(max_length=150)),("field_type",models.CharField(max_length=12,default="text",choices=[("text","Text"),("number","Zahl"),("boolean","Ja / Nein"),("url","URL"),("file","Datei / PDF"),("image","Bild"),("video","Video")])),("section",models.CharField(max_length=20,default="technical",choices=[("general","Allgemeine Informationen"),("technical","Technische Daten"),("applications","Einsatzgebiete"),("media","Dokumente & Medien")])),("position",models.PositiveIntegerField(default=0)),("is_system",models.BooleanField(default=False)),("show_public",models.BooleanField(default=True)),("show_compare",models.BooleanField(default=True)),("archived",models.BooleanField(default=False))],options={"ordering":("section","position","pk")}),
      migrations.CreateModel(name="MachineFieldSetting",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("show_public",models.BooleanField(blank=True,null=True)),("show_compare",models.BooleanField(blank=True,null=True)),("field",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="settings",to="messen.machinefield")),("product",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.CASCADE,to="messen.machineproduct")),("variant",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.CASCADE,to="messen.machinevariant"))]),
      migrations.CreateModel(name="MachineFieldValue",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("text_value",models.TextField(blank=True)),("file_value",models.FileField(blank=True,upload_to="machine-variants/extra/")),("field",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="values",to="messen.machinefield")),("variant",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="custom_values",to="messen.machinevariant"))]),
      migrations.AddConstraint(model_name="machinefieldsetting",constraint=models.UniqueConstraint(fields=("field","product"),name="unique_series_field_setting")),
      migrations.AddConstraint(model_name="machinefieldsetting",constraint=models.UniqueConstraint(fields=("field","variant"),name="unique_variant_field_setting")),
      migrations.AddConstraint(model_name="machinefieldvalue",constraint=models.UniqueConstraint(fields=("field","variant"),name="unique_machine_custom_value")),
      migrations.RunPython(seed,migrations.RunPython.noop),
    ]
