from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("messen", "0027_machinevariant_visible_languages"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name="usedmachine", name="visible_languages", field=models.JSONField("Sichtbare Sprachversionen", default=list, blank=True)),
        migrations.CreateModel(name="UsedMachineRevision", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("action", models.CharField(max_length=100)),
            ("changes", models.JSONField(default=list, blank=True)),
            ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ("machine", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="messen.usedmachine")),
        ], options={"ordering": ["-created_at", "-pk"]}),
    ]
