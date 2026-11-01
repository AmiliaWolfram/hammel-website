from datetime import date
from django.db import migrations

STORIES = [
    dict(title='25 JAHRE (R)EVOLUTION!', published_at=date(2021, 1, 1), category='insights', featured=True,
         teaser='Seit 1996 entwickelt und fertigt HAMMEL Zerkleinerungstechnik in Bad Salzungen. Ein Rückblick auf die Entwicklung vom kleinen Produktionsstandort zum international tätigen Unternehmen.',
         body='Die Geschichte von HAMMEL begann 1996 in Bad Salzungen mit einem kleinen Team und einer Produktionshalle. Über die Jahre wuchsen Fertigung, Produktpalette und internationale Präsenz. Im Mittelpunkt stehen bis heute das Zwei-Wellen-Prinzip und praxisorientierte Recyclinglösungen. Mehr zur Firmengeschichte im Originalbeitrag.',
         external_url='https://www.hammel.de/index.php/de/aktuelles/pressemeldungen/391-25-jahre'),
    dict(title='28 Jahre – Innovation und Engagement', published_at=date(2024, 1, 1), category='events', featured=False,
         teaser='HAMMEL präsentiert auf der IFAT 2024 in München Maschinenlösungen und Weiterentwicklungen, darunter den VB 850 DK und ein Konzept mit elektrischem Direktantrieb.',
         body='Der Messeauftritt zur IFAT 2024 stellt vielseitige Aufbereitungslösungen, das Zwei-Wellen-Prinzip und die Weiterentwicklung elektrohydraulischer Maschinen in den Mittelpunkt. Details zu Maschinen und Messepräsenz im Originalbeitrag.',
         external_url='https://hammel.de/index.php/de/aktuelles/pressemeldungen/477-hammel-ifat-vb850dk'),
    dict(title='(R)EVOLUTION: Neue Schredder', published_at=date(2021, 1, 1), category='innovation', featured=False,
         teaser='Der VB 750 DK Long Version erweitert die Zerkleinerungsmöglichkeiten durch zwei Meter lange Werkzeugwellen und ein überarbeitetes Austragsband.',
         body='HAMMEL stellte 2021 die Long Version des VB 750 DK vor. Verlängerte Werkzeugwellen erleichtern die Verarbeitung sperriger Materialien. Ein Neodymmagnet unterstützt die Metallabscheidung. Technische Details im Originalbeitrag.',
         external_url='https://www.hammel.de/index.php/de/aktuelles/pressemeldungen/417-lv'),
]

def seed(apps, schema_editor):
    NewsArticle = apps.get_model('messen', 'NewsArticle')
    for item in STORIES:
        NewsArticle.objects.get_or_create(external_url=item['external_url'], defaults={**item, 'published': True})

class Migration(migrations.Migration):
    dependencies = [('messen', '0005_newsarticle')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
