# Safe follow-up migration: preserves all translation records and existing indexes.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("translations", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="contenttranslation",
            name="status",
            field=models.CharField(
                choices=[("draft", "Entwurf"), ("review", "Zur Prüfung"), ("published", "Veröffentlicht")],
                default="draft",
                max_length=12,
            ),
        ),
    ]
