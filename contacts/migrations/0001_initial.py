from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(
        name="ContactPerson",
        fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=180,verbose_name="Name")),
            ("department",models.CharField(choices=[(x,x) for x in ("Vertrieb","Service","Einkauf","Konstruktion","Verwaltung","Produktion","Weitere Ansprechpartner")],db_index=True,max_length=80,verbose_name="Bereich")),
            ("role",models.CharField(blank=True,max_length=255,verbose_name="Funktion")),
            ("region",models.TextField(blank=True,verbose_name="Zuständigkeitsbereich")),
            ("phone",models.TextField(blank=True,verbose_name="Telefonnummern (eine pro Zeile)")),
            ("email",models.EmailField(blank=True,max_length=254,verbose_name="E-Mail")),
            ("sort_order",models.PositiveIntegerField(default=100,verbose_name="Reihenfolge")),
            ("published",models.BooleanField(default=True,verbose_name="Auf Website anzeigen")),
        ],
        options={"ordering":["sort_order","name"],"verbose_name":"Ansprechpartner","verbose_name_plural":"Ansprechpartner"},
    )]
