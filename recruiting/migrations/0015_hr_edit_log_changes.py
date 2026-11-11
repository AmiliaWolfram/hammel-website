from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0014_hr_edit_log")]
    operations = [migrations.AddField(model_name="hreditlog", name="changes", field=models.JSONField(default=list, blank=True))]
