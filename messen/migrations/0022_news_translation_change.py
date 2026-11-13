from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("messen", "0021_messe_translation_change"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="NewsTranslationChange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(max_length=2, choices=[("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")])),
                ("field_name", models.CharField(max_length=100)),
                ("field_label", models.CharField(max_length=160)),
                ("old_text", models.TextField(blank=True)),
                ("new_text", models.TextField(blank=True)),
                ("old_status", models.CharField(max_length=30, blank=True)),
                ("new_status", models.CharField(max_length=30, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("article", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="translation_changes", to="messen.newsarticle")),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-pk")},
        ),
    ]
