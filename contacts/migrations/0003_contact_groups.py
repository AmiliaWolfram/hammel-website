from django.db import migrations, models
import django.db.models.deletion

GROUPS = ["Vertrieb", "Service", "Einkauf", "Konstruktion", "Verwaltung", "Produktion"]
ASSIGNMENTS = {
    "Matthias Führer":"Service", "Nico Heidrich":"Service",
    "Jennifer Kirchner":"Service", "Kerstin Fischer":"Service",
    "Tobias Kürschner":"Einkauf", "Chris Ehlert":"Einkauf",
    "Karsten Franke":"Konstruktion", "Julian Senf":"Verwaltung",
    "Dirk Schlotzhauer":"Produktion", "Mike-Peter Beerbaum":"Produktion",
}

def assign_groups(apps,schema_editor):
    Group=apps.get_model("contacts","ContactGroup")
    Person=apps.get_model("contacts","ContactPerson")
    groups={name:Group.objects.create(name=name,sort_order=i*10) for i,name in enumerate(GROUPS)}
    for person in Person.objects.all():
        name=ASSIGNMENTS.get(person.name,person.department)
        if name not in groups: continue
        person.group=groups[name]
        person.save(update_fields=["group"])

def reverse_groups(apps,schema_editor):
    Person=apps.get_model("contacts","ContactPerson")
    for p in Person.objects.select_related("group"):
        p.department=p.group.name if p.group_id else "Vertrieb"
        p.save(update_fields=["department"])

class Migration(migrations.Migration):
    dependencies=[("contacts","0002_seed_contacts")]
    operations=[
        migrations.CreateModel(name="ContactGroup",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=100,unique=True,verbose_name="Gruppenname")),
            ("sort_order",models.PositiveIntegerField(default=100,verbose_name="Reihenfolge")),
            ("published",models.BooleanField(default=True,verbose_name="Auf Website anzeigen")),
        ],options={"ordering":["sort_order","id"],"verbose_name":"Kontaktgruppe","verbose_name_plural":"Kontaktgruppen"}),
        migrations.AddField(model_name="contactperson",name="group",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="people",to="contacts.contactgroup",verbose_name="Gruppe")),
        migrations.RunPython(assign_groups,reverse_groups),
        migrations.RemoveField(model_name="contactperson",name="department"),
    ]
