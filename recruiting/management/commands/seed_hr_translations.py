"""Seed carefully reviewed starter translations without overwriting editorial changes."""
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from recruiting.models import HRTextBlock
from translations.models import ContentTranslation
from translations.services import fingerprint

STARTER = {
 'Abwechslungsreiche Aufgaben': ('Varied responsibilities','Missions variées','Tareas variadas','Attività diversificate'),
 'Analytisches Denken': ('Analytical thinking','Esprit analytique','Pensamiento analítico','Pensiero analitico'),
 'Analytisches Verständnis': ('Analytical aptitude','Capacité d’analyse','Capacidad de análisis','Capacità di analisi'),
 'Ausbildungsvergütung': ('Apprenticeship remuneration','Rémunération de formation','Remuneración durante la formación','Retribuzione durante la formazione'),
 'Aussagekräftige Arbeitsproben': ('Relevant work samples','Exemples de travaux pertinents','Muestras de trabajo representativas','Esempi significativi di lavori svolti'),
 'Gute Deutschkenntnisse': ('Good German language skills','Bonne maîtrise de l’allemand','Buenos conocimientos de alemán','Buona conoscenza del tedesco'),
 'Fließende Deutschkenntnisse': ('Fluent German','Maîtrise courante de l’allemand','Dominio fluido del alemán','Ottima padronanza del tedesco'),
 'Grundkenntnisse in MS Office': ('Basic knowledge of MS Office','Connaissances de base de MS Office','Conocimientos básicos de MS Office','Conoscenze di base di MS Office'),
 'Organisation kaufmännischer Abläufe': ('Organization of commercial processes','Organisation des processus commerciaux','Organización de procesos comerciales','Organizzazione dei processi commerciali'),
 'Mit Fachbereichen zusammenarbeiten': ('Collaborate with specialist departments','Collaborer avec les services spécialisés','Colaborar con los departamentos especializados','Collaborare con i reparti specializzati'),
 'Mit Außendienst, Logistik und Buchhaltung zusammenarbeiten': ('Collaborate with field sales, logistics and accounting','Collaborer avec le service commercial externe, la logistique et la comptabilité','Colaborar con ventas externas, logística y contabilidad','Collaborare con il servizio vendite esterno, la logistica e la contabilità'),
}
class Command(BaseCommand):
    help = 'Add starter translations for existing HR checkbox options, without overwriting existing translations.'
    @transaction.atomic
    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(HRTextBlock)
        count = 0
        for source, texts in STARTER.items():
            for block in HRTextBlock.objects.filter(text=source):
                for language, value in zip(('en','fr','es','it'), texts):
                    _, created = ContentTranslation.objects.get_or_create(content_type=ct, object_id=block.pk, field_name='text', language=language, defaults={'text':value,'status':'review','source_hash':fingerprint(block.text)})
                    count += int(created)
        self.stdout.write(self.style.SUCCESS(f'{count} new translations added. Existing translations preserved.'))
