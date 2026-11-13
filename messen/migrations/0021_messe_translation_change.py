from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("messen", "0020_merge_showcase_variant"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="MesseTranslationChange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(choices=[("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")], max_length=2)),
                ("field_name", models.CharField(max_length=100)),
                ("field_label", models.CharField(max_length=160)),
                ("old_text", models.TextField(blank=True)),
                ("new_text", models.TextField(blank=True)),
                ("old_status", models.CharField(blank=True, max_length=30)),
                ("new_status", models.CharField(blank=True, max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("messe", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="translation_changes", to="messen.messe")),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-pk")},
        ),
    ]
