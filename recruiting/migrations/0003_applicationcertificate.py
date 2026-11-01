from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("recruiting", "0002_applicationdepartment")]

    operations = [
        migrations.CreateModel(
            name="ApplicationCertificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="hr/certificates/%Y/%m/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certificate_files", to="recruiting.application")),
            ],
            options={"verbose_name": "Zeugnis oder Zertifikat", "verbose_name_plural": "Zeugnisse und Zertifikate"},
        ),
    ]
