from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("recruiting","0008_vacancy_skills_textblocks")]
    operations=[migrations.AddField(model_name="hrtextblock",name="profession",field=models.CharField(max_length=40,blank=True,default="",help_text="Leer = für alle Berufsprofile"))]
