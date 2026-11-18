import hashlib
from django.db import models
from django.contrib.contenttypes.models import ContentType
from .models import ContentTranslation

# Never translate URLs, files, numeric values, technical identifiers or personal application data.
EXCLUDED = {"slug", "email", "phone", "url", "external_url", "image_url", "video_url", "model_name", "serial_number", "technical_data", "notes", "country", "city", "booth", "location", "employment_type", "engine", "power", "weight", "operating_hours"}
ALLOWED_MODELS = {
    "recruiting": {"vacancy", "hrtip", "applicationdepartment", "vacancydepartment", "hrtextblock"},
    "messen": {"messe", "newsarticle", "usedmachine", "machineproduct", "machinevariant", "recyclingarea", "recyclingmaterial", "homepageShowcase".lower()},
    "contacts": {"contactgroup"},
    "partners": {"partner"},
}
def fields_for(obj):
    if obj._meta.model_name not in ALLOWED_MODELS.get(obj._meta.app_label, set()):
        return []
    return [f for f in obj._meta.fields if isinstance(f, (models.CharField, models.TextField)) and not isinstance(f, (models.SlugField, models.URLField, models.EmailField)) and f.name not in EXCLUDED and not f.choices and f.editable]

def fingerprint(value):
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()

def translated(obj, field_name, language="de"):
    original = getattr(obj, field_name)
    if language == "de" or field_name not in {f.name for f in fields_for(obj)}:
        return original
    if obj._meta.app_label == "messen" and obj._meta.model_name in {"messe", "newsarticle"}:
        if not (getattr(obj, "language_visibility", None) or {}).get(language, False):
            return original
    if obj._meta.app_label == "messen" and obj._meta.model_name == "machinevariant":
        visibility = getattr(obj, "visible_languages", None)
        if visibility is not None and language not in visibility:
            return original
    entry = ContentTranslation.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk, field_name=field_name, language=language, status="published").first()
    return entry.text if entry and entry.source_hash == fingerprint(original) and entry.text.strip() else original


# Shared inline editing API. The original German model fields remain authoritative.
def inline_payload(obj, form=None):
    if obj is None or obj.pk is None:
        return None
    from django.contrib.contenttypes.models import ContentType
    from .models import LANGUAGES
    names = {f.name for f in fields_for(obj)}
    if form is not None:
        names &= set(form.fields)
    if not names:
        return None
    ct = ContentType.objects.get_for_model(obj)
    entries = ContentTranslation.objects.filter(content_type=ct, object_id=obj.pk, field_name__in=names)
    lookup = {(e.language, e.field_name): e for e in entries}
    rows = []
    for f in fields_for(obj):
        if f.name not in names:
            continue
        original = str(getattr(obj, f.name) or "")
        versions = {}
        for code, _ in LANGUAGES:
            if code == "de":
                continue
            entry = lookup.get((code, f.name))
            versions[code] = {"text": entry.text if entry else "", "status": entry.status if entry else "draft", "stale": bool(entry and entry.source_hash != fingerprint(original))}
        rows.append({"name": f.name, "label": str(form.fields[f.name].label or f.verbose_name) if form else str(f.verbose_name), "versions": versions})
    return {"rows": rows}


def save_inline(request, obj, form=None):
    """Persist all language tabs atomically with the calling form save.

    Missing inline payload means no change (backwards compatible forms).
    """
    import json
    from django.core.exceptions import ValidationError
    from django.contrib.contenttypes.models import ContentType
    raw = request.POST.get("inline_translations")
    if not raw:
        return
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Ungültige Sprachdaten") from exc
    if not isinstance(data, dict):
        raise ValidationError("Ungültige Sprachdaten")
    names = {f.name for f in fields_for(obj)}
    if form is not None:
        names &= set(form.fields)
    ct = ContentType.objects.get_for_model(obj)
    for language, fields in data.items():
        if language not in {"en", "fr", "es", "it"} or not isinstance(fields, dict):
            raise ValidationError("Ungültige Sprache")
        for name, content in fields.items():
            if not content.get("dirty"):
                continue
            if name not in names or not isinstance(content, dict):
                raise ValidationError("Ungültiges Übersetzungsfeld")
            value = content.get("text", "")
            status = content.get("status", "draft")
            if not isinstance(value, str) or len(value) > 30000 or status not in {"draft", "review", "published"}:
                raise ValidationError("Ungültiger Übersetzungstext oder Status")
            ContentTranslation.objects.update_or_create(
                content_type=ct, object_id=obj.pk, field_name=name, language=language,
                defaults={"text": value, "status": status if value.strip() else "draft", "source_hash": fingerprint(getattr(obj, name)), "updated_by": request.user},
            )


# Reuse approved translations of predefined HR checkbox suggestions.
# This never invokes machine translation and never publishes a vacancy translation.
HR_BUILDER_FIELDS = ("responsibilities", "hard_skills", "soft_skills", "benefits")


def fill_vacancy_from_library(vacancy):
    """Prefill vacancy drafts from approved library phrases, preserving manual edits.

    Custom lines remain German placeholders for manual translation. Generated drafts
    have updated_by=None; once a human edits them they are never overwritten.
    """
    from recruiting.models import HRTextBlock
    if not vacancy.pk:
        return
    source_lines = {}
    for category in HR_BUILDER_FIELDS:
        source_lines[category] = [line.strip() for line in (getattr(vacancy, category) or "").splitlines() if line.strip()]
    all_lines = {line for lines in source_lines.values() for line in lines}
    if not all_lines:
        return
    blocks = list(HRTextBlock.objects.filter(active=True, text__in=all_lines))
    block_ct = ContentType.objects.get_for_model(HRTextBlock)
    vacancy_ct = ContentType.objects.get_for_model(vacancy)
    library = ContentTranslation.objects.filter(
        content_type=block_ct, object_id__in=[b.pk for b in blocks],
        field_name="text", status="published", language__in=("en", "fr", "es", "it"),
    )
    block_lookup = {(b.pk, b.category, b.text): b for b in blocks}
    approved = {}
    for entry in library:
        for block in blocks:
            if entry.object_id == block.pk and entry.source_hash == fingerprint(block.text) and entry.text.strip():
                approved[(block.category, block.text, entry.language)] = entry.text.strip()
                break
    for category, lines in source_lines.items():
        original = getattr(vacancy, category)
        for lang in ("en", "fr", "es", "it"):
            existing = ContentTranslation.objects.filter(
                content_type=vacancy_ct, object_id=vacancy.pk,
                field_name=category, language=lang,
            ).first()
            if existing and existing.updated_by_id is not None:
                continue
            # Do not replace previously generated drafts if source is unchanged.
            if existing and existing.source_hash == fingerprint(original):
                continue
            rendered = [approved.get((category, line, lang), line) for line in lines]
            if not any(approved.get((category, line, lang)) for line in lines):
                continue
            # Untranslated individual lines are visibly retained in German, and
            # the result is ALWAYS a draft requiring a human review.
            ContentTranslation.objects.update_or_create(
                content_type=vacancy_ct, object_id=vacancy.pk,
                field_name=category, language=lang,
                defaults={"text": "\n".join(rendered), "status": "draft",
                          "source_hash": fingerprint(original), "updated_by": None},
            )
