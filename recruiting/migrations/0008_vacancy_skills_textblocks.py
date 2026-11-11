from django.db import migrations, models

def seed(apps, schema_editor):
    Block = apps.get_model("recruiting", "HRTextBlock")
    examples = {
        "responsibilities": ["Unterstützung im Einkauf und Vertrieb", "Bearbeitung von Kundenanfragen", "Organisation kaufmännischer Abläufe", "Zusammenarbeit mit internationalen Partnern"],
        "hard_skills": ["Grundkenntnisse in MS Office", "Interesse an kaufmännischen Prozessen", "Technisches Verständnis", "Gute Deutschkenntnisse"],
        "soft_skills": ["Teamfähigkeit", "Zuverlässigkeit", "Kommunikationsfreude", "Eigeninitiative", "Sorgfältige Arbeitsweise"],
        "benefits": ["Praxisnahe Einarbeitung", "Einblicke in verschiedene Abteilungen", "Abwechslungsreiche Aufgaben"],
    }
    for category, texts in examples.items():
        for text in texts:
            Block.objects.get_or_create(category=category, text=text)

class Migration(migrations.Migration):
    dependencies = [("recruiting", "0007_demo_ausbildung_content")]
    operations = [
        migrations.AddField(model_name="vacancy", name="hard_skills", field=models.TextField(blank=True, help_text="Fachliche Kenntnisse, eine pro Zeile")),
        migrations.AddField(model_name="vacancy", name="soft_skills", field=models.TextField(blank=True, help_text="Persönliche Stärken, eine pro Zeile")),
        migrations.CreateModel(name="HRTextBlock", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("category", models.CharField(max_length=32, choices=[("responsibilities","Deine Aufgaben"),("hard_skills","Fachliche Kenntnisse"),("soft_skills","Persönliche Stärken"),("benefits","Das bieten wir")])),
            ("text", models.CharField(max_length=300)),
            ("active", models.BooleanField(default=True)),
        ], options={"ordering":["category","text"]}),
        migrations.AddConstraint(model_name="hrtextblock", constraint=models.UniqueConstraint(fields=["category","text"], name="hr_textblock_category_text_unique")),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
