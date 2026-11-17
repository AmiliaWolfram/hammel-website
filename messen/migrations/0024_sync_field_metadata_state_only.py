"""Synchronize historical Django field metadata without database schema changes."""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('messen', '0023_messen_news_language_visibility')]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
            migrations.AlterField(model_name='homepageshowcase', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinefield', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinefieldsetting', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinefieldvalue', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinevariantdraft', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinevariantphoto', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='machinevariantrevision', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='usedmachine', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='usedmachinephoto', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True))
            ],
        ),
    ]
