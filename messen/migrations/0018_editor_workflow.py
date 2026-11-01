from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
 dependencies=[("messen","0017_machine_field_management")]
 operations=[
  migrations.CreateModel(name="MachineVariantPhoto",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("image",models.ImageField(upload_to="machine-variants/gallery/")),("caption",models.CharField(max_length=180,blank=True)),("position",models.PositiveIntegerField(default=0)),("is_cover",models.BooleanField(default=False)),("variant",models.ForeignKey(to="messen.machinevariant",related_name="gallery",on_delete=django.db.models.deletion.CASCADE))],options={"ordering":("position","pk")}),
  migrations.CreateModel(name="MachineVariantRevision",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("created_at",models.DateTimeField(auto_now_add=True)),("action",models.CharField(max_length=30,default="saved")),("snapshot",models.JSONField(default=dict)),("author",models.ForeignKey(to="auth.user",null=True,on_delete=django.db.models.deletion.SET_NULL)),("variant",models.ForeignKey(to="messen.machinevariant",related_name="revisions",on_delete=django.db.models.deletion.CASCADE))],options={"ordering":("-created_at",)}),
  migrations.CreateModel(name="MachineVariantDraft",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("updated_at",models.DateTimeField(auto_now=True)),("values",models.JSONField(default=dict)),("author",models.ForeignKey(to="auth.user",null=True,on_delete=django.db.models.deletion.SET_NULL)),("variant",models.OneToOneField(to="messen.machinevariant",related_name="editing_draft",on_delete=django.db.models.deletion.CASCADE))]),
 ]
