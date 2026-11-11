from django.db import models
from django.contrib.contenttypes.models import ContentType

LANGUAGES = [("de", "Deutsch"), ("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")]
STATUSES = [("draft", "Entwurf"), ("review", "Zur Prüfung"), ("published", "Veröffentlicht")]

class ContentTranslation(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    field_name = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUSES, default="draft")
    source_hash = models.CharField(max_length=64, blank=True)
    updated_by = models.ForeignKey("auth.User", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["content_type", "object_id", "field_name", "language"], name="unique_content_translation")]
        indexes = [models.Index(fields=["content_type", "object_id", "language"], name="trans_ct_obj_lang_idx")]
