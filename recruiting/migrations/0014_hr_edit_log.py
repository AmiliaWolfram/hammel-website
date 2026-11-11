from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0013_clean_imported_intro"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.CreateModel(name="HREditLog", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("action", models.CharField(max_length=40)), ("detail", models.CharField(blank=True, max_length=250)), ("created_at", models.DateTimeField(auto_now_add=True)), ("user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")), ("vacancy", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="edit_history", to="recruiting.vacancy"))], options={"ordering": ["-created_at"]})]
