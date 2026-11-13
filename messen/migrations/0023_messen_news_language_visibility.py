from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("messen", "0022_news_translation_change")]
    operations = [
        migrations.AddField(model_name="messe", name="language_visibility", field=models.JSONField(blank=True, default=dict, verbose_name="Sichtbare Sprachversionen")),
        migrations.AddField(model_name="newsarticle", name="language_visibility", field=models.JSONField(blank=True, default=dict, verbose_name="Sichtbare Sprachversionen")),
    ]
