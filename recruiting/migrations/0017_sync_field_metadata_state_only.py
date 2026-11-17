"""Synchronize historical Django field metadata without database schema changes."""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('recruiting', '0016_vacancy_visible_languages')]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
            migrations.AlterField(model_name='application', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='applicationdepartment', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='hrtextblock', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='hrtip', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='vacancy', name='id', field=models.BigAutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
            migrations.AlterField(model_name='application', name='notes', field=models.TextField(blank=True, help_text="Nur für HR")),
            migrations.AlterField(model_name='vacancy', name='benefits', field=models.TextField(blank=True, help_text="Ein Vorteil pro Zeile")),
            migrations.AlterField(model_name='vacancy', name='requirements', field=models.TextField(blank=True, help_text="Eine Anforderung pro Zeile")),
            migrations.AlterField(model_name='vacancy', name='responsibilities', field=models.TextField(blank=True, help_text="Eine Aufgabe pro Zeile"))
            ],
        ),
    ]
