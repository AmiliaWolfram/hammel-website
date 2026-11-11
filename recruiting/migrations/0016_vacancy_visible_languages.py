from django.db import migrations, models

def initialize_visibility(apps, schema_editor):
    Vacancy = apps.get_model("recruiting", "Vacancy")
    # Keep all previously published German vacancies visible.
    for vacancy in Vacancy.objects.filter(published=True).iterator():
        vacancy.visible_languages = ["de"]
        vacancy.save(update_fields=["visible_languages"])

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0015_hr_edit_log_changes")]
    operations = [
        migrations.AddField(model_name="vacancy", name="visible_languages", field=models.JSONField(default=list, blank=True, help_text="Öffentlich sichtbare Sprachversionen (de, en, fr, es, it)")),
        migrations.RunPython(initialize_visibility, migrations.RunPython.noop),
    ]
