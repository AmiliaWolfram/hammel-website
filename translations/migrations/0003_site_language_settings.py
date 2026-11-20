from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("translations", "0002_rename_trans_ct_obj_lang_idx_translation_content_363ddd_idx_and_more")]
    operations = [migrations.CreateModel(name="SiteLanguageSettings", fields=[("singleton_key", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)), ("enabled_languages", models.JSONField(default=list)), ("updated_at", models.DateTimeField(auto_now=True))])]
