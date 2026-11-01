from datetime import date
from django.db import migrations


def add_upcoming_messen(apps, schema_editor):
    Messe = apps.get_model("messen", "Messe")
    events = [
        {"title": "HAMMEL Messe Málaga 2026", "start_date": date(2026, 10, 26), "end_date": date(2026, 10, 27), "city": "Málaga", "country": "Spanien", "booth": "Stand B4"},
        {"title": "HAMMEL Messe Rimini 2026", "start_date": date(2026, 11, 3), "end_date": date(2026, 11, 6), "city": "Rimini", "country": "Italien", "booth": "Halle A3 / Stand 209–108"},
        {"title": "HAMMEL Messe Luzern 2027", "start_date": date(2027, 1, 21), "end_date": date(2027, 1, 23), "city": "Luzern", "country": "Schweiz", "booth": "Halle 2 / Stand D42"},
    ]
    for event in events:
        Messe.objects.update_or_create(
            start_date=event["start_date"], city=event["city"],
            defaults={**event, "published": True},
        )


class Migration(migrations.Migration):
    dependencies = [("messen", "0003_messephoto")]
    operations = [migrations.RunPython(add_upcoming_messen, migrations.RunPython.noop)]
