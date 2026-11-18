from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("messen", "0025_four_recycling_areas")]
    operations = [migrations.RemoveField(model_name="machinevariant", name="datasheet_url")]
