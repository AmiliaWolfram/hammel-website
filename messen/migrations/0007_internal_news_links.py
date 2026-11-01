from django.db import migrations

def internalize(apps, schema_editor):
    Article = apps.get_model("messen", "NewsArticle")
    replacements = {
        "25 JAHRE (R)EVOLUTION!": "Seit 1996 entwickelt und fertigt HAMMEL Recyclingtechnik in Bad Salzungen. Aus einem kleinen Produktionsstandort entwickelte sich ein international tätiges Unternehmen. Bis heute prägen das Zwei-Wellen-Prinzip, technische Weiterentwicklung und praxisnahe Lösungen die Unternehmensgeschichte.",
        "28 Jahre – Innovation und Engagement": "Bei der IFAT 2024 in München präsentierte HAMMEL Lösungen für die Aufbereitung unterschiedlicher Materialien. Im Mittelpunkt standen unter anderem der VB 850 DK, das bewährte Zwei-Wellen-Prinzip und ein Konzept mit elektrischem Direktantrieb.",
        "(R)EVOLUTION: Neue Schredder": "Mit dem VB 750 DK Long Version entwickelte HAMMEL die Vorzerkleinerung weiter. Zwei Meter lange Werkzeugwellen erweitern die Einsatzmöglichkeiten für sperrige Materialien. Ein überarbeitetes Austragsband und die Metallabscheidung ergänzen das Maschinenkonzept.",
    }
    for article in Article.objects.all():
        fields = []
        if article.external_url:
            article.external_url = ""
            fields.append("external_url")
        # Replace only the original seeded teaser-style placeholder body; leave user edits untouched.
        if article.title in replacements and ("Originalbeitrag" in article.body or "Firmengeschichte im Originalbeitrag" in article.body):
            article.body = replacements[article.title]
            fields.append("body")
        if fields:
            article.save(update_fields=fields)

class Migration(migrations.Migration):
    dependencies = [("messen", "0006_seed_hammel_stories")]
    operations = [migrations.RunPython(internalize, migrations.RunPython.noop)]
