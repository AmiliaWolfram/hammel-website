from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('contenttypes', '0002_remove_content_type_name')]
    operations = [
        migrations.CreateModel(name='ContentTranslation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('object_id', models.PositiveBigIntegerField()),
            ('field_name', models.CharField(max_length=100)),
            ('language', models.CharField(choices=[('de','Deutsch'),('en','English'),('fr','Français'),('es','Español'),('it','Italiano')], max_length=2)),
            ('text', models.TextField(blank=True)),
            ('status', models.CharField(choices=[('draft','In Bearbeitung'),('review','Zur Prüfung'),('published','Veröffentlicht')], default='draft', max_length=12)),
            ('source_hash', models.CharField(blank=True, max_length=64)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
        ], options={'indexes': [models.Index(fields=['content_type','object_id','language'], name='trans_ct_obj_lang_idx')], 'constraints': [models.UniqueConstraint(fields=('content_type','object_id','field_name','language'), name='unique_content_translation')]})
    ]
