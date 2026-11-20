from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .models import ContentTranslation, LANGUAGES, SiteLanguageSettings
from .services import ALLOWED_MODELS, fields_for, fingerprint

@login_required
@require_http_methods(["GET", "POST"])
def edit(request, app_label, model_name, pk):
    if model_name not in ALLOWED_MODELS.get(app_label, set()):
        raise Http404
    ct = get_object_or_404(ContentType, app_label=app_label, model=model_name)
    model = ct.model_class()
    if model is None:
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    if not request.user.has_perm(f"{app_label}.change_{model_name}"):
        raise PermissionDenied
    fields = fields_for(obj)
    if not fields:
        raise Http404("Keine übersetzbaren Felder")
    active = SiteLanguageSettings.enabled()
    available = [(code, label) for code, label in LANGUAGES[1:] if code in active]
    inactive = [(code, label) for code, label in LANGUAGES[1:] if code not in active]
    show_inactive = request.GET.get("show_inactive") == "1"
    language = request.GET.get("lang", "en")
    if language not in {code for code, _ in LANGUAGES if code != "de"}:
        language = "en"
    existing = {x.field_name: x for x in ContentTranslation.objects.filter(content_type=ct, object_id=pk, language=language)}
    if request.method == "POST":
        updates = []
        for field in fields:
            text = request.POST.get("translation_" + field.name, "")
            if len(text) > 30000:
                messages.error(request, "Ein Text ist zu lang (maximal 30.000 Zeichen).")
                return redirect(request.path + "?lang=" + language)
            status = request.POST.get("status_" + field.name, "draft")
            if status not in {"draft", "review", "published"}:
                status = "draft"
            previous = existing.get(field.name)
            original_hash = fingerprint(getattr(obj, field.name))
            # Only confirm a changed source when explicitly checked, or when the translation text changes.
            confirmed = request.POST.get("confirm_" + field.name) == "on"
            changed = previous is None or previous.text != text
            source_hash = original_hash if changed or confirmed else previous.source_hash
            if previous and previous.source_hash != original_hash and not (changed or confirmed) and status == "published":
                status = "review"
            updates.append((field, text, status, source_hash))
        audit_changes = []
        if app_label == "recruiting" and model_name == "vacancy":
            for field, new_text, new_status, _ in updates:
                old_item = existing.get(field.name)
                old_text = old_item.text if old_item else ""
                old_status = old_item.status if old_item else "draft"
                if old_text != new_text:
                    audit_changes.append({"field": f"{language.upper()} · {field.verbose_name}", "old": old_text, "new": new_text})
                if old_status != new_status:
                    audit_changes.append({"field": f"{language.upper()} · {field.verbose_name} (Status)", "old": old_status, "new": new_status})
        with transaction.atomic():
            for field, text, status, source_hash in updates:
                ContentTranslation.objects.update_or_create(
                    content_type=ct, object_id=pk, field_name=field.name, language=language,
                    defaults={"text": text, "status": status if text.strip() else "draft",
                              "source_hash": source_hash, "updated_by": request.user},
                )
            if app_label == "recruiting" and model_name == "vacancy" and audit_changes:
                from recruiting.models import HREditLog
                HREditLog.objects.create(
                    vacancy=obj, user=request.user, action="translation",
                    detail=f"Sprachversion {language.upper()} gespeichert", changes=audit_changes,
                )
        messages.success(request, "Sprachversion gespeichert")
        return redirect(request.path + "?lang=" + language)
    rows = []
    for field in fields:
        original = str(getattr(obj, field.name) or "")
        item = existing.get(field.name)
        rows.append({"name": field.name, "label": str(field.verbose_name).capitalize(), "original": original, "text": item.text if item else "", "status": item.status if item else "draft", "stale": bool(item and item.text.strip() and item.source_hash != fingerprint(original)), "updated_at": item.updated_at if item else None, "updated_by": item.updated_by if item else None})
    return render(request, "translations/editor.html", {"object": obj, "rows": rows, "language": language, "languages": available + (inactive if show_inactive else []), "inactive_languages": inactive, "show_inactive": show_inactive, "portal": "HRPortal" if app_label == "recruiting" else "Vertriebsportal", "base_template": "translations/hr_portal_base.html" if app_label == "recruiting" else "translations/editor_sales_base.html", "is_hr": app_label == "recruiting", "autosave_url": __import__("django.urls", fromlist=["reverse"]).reverse("translation_autosave", args=[app_label, model_name, pk]), "is_vacancy": app_label == "recruiting" and model_name == "vacancy", "hr_kind": {"hrtip":"tip", "applicationdepartment":"department", "vacancydepartment":"job_department"}.get(model_name) if app_label == "recruiting" else None})

@login_required
def catalog(request, portal):
    if portal not in {"hr", "vertrieb"}:
        raise Http404
    apps = ["recruiting"] if portal == "hr" else ["messen", "contacts", "partners"]
    from .services import fingerprint
    active_languages = [(code, label) for code, label in LANGUAGES[1:] if code in SiteLanguageSettings.enabled()]
    groups = []
    missing_total = stale_total = translated_total = published_total = review_total = draft_total = total_fields = 0
    language_stats = {code: {"code": code.upper(), "label": label, "total": 0, "translated": 0, "published": 0, "missing": 0, "draft": 0, "review": 0} for code, label in active_languages}
    from django.urls import reverse
    editor_routes = {
        ("recruiting", "vacancy"): ("hr_edit", ["vacancy"]),
        ("recruiting", "hrtip"): ("hr_edit", ["tip"]),
    }
    for app_label in apps:
        for model_name in sorted(ALLOWED_MODELS.get(app_label, set())):
            ct = ContentType.objects.filter(app_label=app_label, model=model_name).first()
            if not ct or not request.user.has_perm(f"{app_label}.change_{model_name}"):
                continue
            model = ct.model_class()
            if model is None:
                continue
            objects = list(model.objects.all().order_by("-pk")[:150])
            items = []
            group_counts = {"total": 0, "missing": 0, "draft": 0, "review": 0, "translated": 0, "stale": 0}
            for obj in objects:
                fields = fields_for(obj)
                if not fields:
                    continue
                existing = {(x.field_name, x.language): x for x in ContentTranslation.objects.filter(content_type=ct, object_id=obj.pk)}
                missing, stale = [], []
                object_total = object_translated = object_published = object_review = object_draft = 0
                for language, _ in active_languages:
                    for field in fields:
                        original = getattr(obj, field.name) or ""
                        if not str(original).strip():
                            continue
                        total_fields += 1
                        group_counts["total"] += 1
                        object_total += 1
                        language_stats[language]["total"] += 1
                        entry = existing.get((field.name, language))
                        if not entry or not entry.text.strip():
                            missing.append(language.upper())
                            missing_total += 1
                            language_stats[language]["missing"] += 1
                            group_counts["missing"] += 1
                            continue
                        translated_total += 1
                        object_translated += 1
                        language_stats[language]["translated"] += 1
                        if entry.source_hash != fingerprint(original):
                            stale.append(language.upper())
                            stale_total += 1
                            group_counts["stale"] += 1
                        if entry.status == "published":
                            published_total += 1
                            group_counts["translated"] += 1
                            object_published += 1
                            language_stats[language]["published"] += 1
                        elif entry.status == "review":
                            review_total += 1
                            object_review += 1
                            language_stats[language]["review"] += 1
                            group_counts["review"] += 1
                        else:
                            draft_total += 1
                            object_draft += 1
                            language_stats[language]["draft"] += 1
                            group_counts["draft"] += 1
                route = editor_routes.get((app_label, model_name))
                try:
                    url = reverse(route[0], args=[*route[1], obj.pk]) if route else reverse("translation_edit", args=[app_label, model_name, obj.pk])
                except Exception:
                    url = reverse("translation_edit", args=[app_label, model_name, obj.pk])
                items.append({"title": str(obj), "url": url, "missing": sorted(set(missing)), "stale": sorted(set(stale)), "missing_count": len(missing), "stale_count": len(stale), "total": object_total, "translated": object_translated, "published": object_published, "complete": object_total > 0 and object_translated == object_total, "needs_review": bool(stale) or object_review > 0, "review_count": object_review, "draft_count": object_draft})
            if items:
                # Anzeigenamen zentral festlegen: keine technischen Django-Modellnamen im HRPortal.
                group_display_names = {
                    ("recruiting", "applicationarea"): "Bewerbungsbereiche",
                    ("recruiting", "hrtextblock"): "HR-Textbausteine",
                    ("recruiting", "hrtip"): "Bewerbungstipps",
                    ("recruiting", "vacancy"): "Stellenangebote",
                    ("recruiting", "vacancydepartment"): "Stellenbereiche",
                }
                display_name = group_display_names.get(
                    (app_label, model_name), str(model._meta.verbose_name_plural)
                )
                groups.append({"label": display_name, "objects": items, **group_counts, "percent": round(100 * group_counts["translated"] / group_counts["total"]) if group_counts["total"] else 0})
    for stat in language_stats.values():
        stat["percent"] = round(100 * stat["translated"] / stat["total"]) if stat["total"] else 0
    return render(request, "translations/catalog.html", {
        "groups": groups, "portal": "HRPortal" if portal == "hr" else "Vertriebsportal",
        "missing_total": missing_total, "stale_total": stale_total, "translated_total": translated_total,
        "published_total": published_total, "review_total": review_total, "draft_total": draft_total,
        "total_fields": total_fields, "progress_percent": round(100 * published_total / total_fields) if total_fields else 0,
        "language_stats": list(language_stats.values()), "portal_key": portal,
        "base_template": "translations/hr_portal_base.html" if portal == "hr" else "messen/base.html",
    })


@login_required
@require_http_methods(["GET", "POST"])
def hr_blocks(request):
    """Manual translations for existing HR text blocks; save all four languages at once."""
    from django.db import transaction
    from recruiting.models import HRTextBlock
    from .services import fingerprint
    if not (request.user.has_perm("recruiting.change_hrtextblock") or request.user.has_perm("recruiting.change_vacancy")):
        raise PermissionDenied
    enabled_codes = set(SiteLanguageSettings.enabled())
    show_inactive = request.GET.get("show_inactive") == "1"
    active_languages = [(code, label) for code, label in LANGUAGES[1:] if code in enabled_codes]
    inactive_languages = [(code, label) for code, label in LANGUAGES[1:] if code not in enabled_codes]
    visible_languages = active_languages + (inactive_languages if show_inactive else [])
    ct = ContentType.objects.get_for_model(HRTextBlock)
    profession = request.GET.get("profession", "")
    category = request.GET.get("category", "")
    queryset = HRTextBlock.objects.all()
    if profession:
        queryset = queryset.filter(profession=profession)
    if category in dict(HRTextBlock.CATEGORY):
        queryset = queryset.filter(category=category)
    blocks = list(queryset.order_by("profession", "category", "text")[:500])
    ids = [b.pk for b in blocks]
    if request.method == "POST":
        approve_id = request.POST.get("approve_block")
        if approve_id:
            if not request.user.has_perm("recruiting.change_hrtextblock"):
                raise PermissionDenied
            block = get_object_or_404(HRTextBlock, pk=approve_id)
            block.active = True
            block.save(update_fields=["active"])
            messages.success(request, "Deutscher Originaltext freigegeben. Übersetzungen können jetzt gepflegt werden.")
            return redirect(request.get_full_path())
        if len(request.POST) > 2500:
            messages.error(request, "Zu viele Felder. Bitte filtern Sie die Textbausteine.")
            return redirect(request.get_full_path())
        with transaction.atomic():
            for block in blocks:
                if not block.active:
                    continue
                for language, _ in visible_languages:
                    key = f"block_{block.pk}_{language}"
                    if key not in request.POST:
                        continue
                    value = request.POST[key].strip()
                    if len(value) > 300:
                        messages.error(request, "Ein Textbaustein darf höchstens 300 Zeichen enthalten.")
                        return redirect(request.get_full_path())
                    status = request.POST.get(f"status_{block.pk}_{language}", "draft")
                    if status not in {"draft", "review", "published"}:
                        status = "draft"
                    ContentTranslation.objects.update_or_create(
                        content_type=ct, object_id=block.pk, field_name="text", language=language,
                        defaults={"text": value, "status": status if value else "draft", "source_hash": fingerprint(block.text), "updated_by": request.user},
                    )
        messages.success(request, "Alle Sprachversionen gespeichert.")
        return redirect(request.get_full_path())
    lookup = {(x.object_id, x.language): x for x in ContentTranslation.objects.filter(content_type=ct, object_id__in=ids, field_name="text")}
    rows = []
    missing = stale = 0
    for block in blocks:
        versions = []
        for language, label in visible_languages:
            entry = lookup.get((block.pk, language))
            outdated = bool(entry and entry.text and entry.source_hash != fingerprint(block.text))
            if not entry or not entry.text.strip(): missing += 1
            if outdated: stale += 1
            versions.append({"code": language, "label": label, "text": entry.text if entry else "", "status": entry.status if entry else "draft", "stale": outdated})
        rows.append({"block": block, "versions": versions})
    # Navigation counts respect the selected profession, not the category filter.
    category_base = HRTextBlock.objects.all()
    if profession:
        category_base = category_base.filter(profession=profession)
    category_navigation = [
        {"key": key, "label": label, "count": category_base.filter(category=key).count()}
        for key, label in HRTextBlock.CATEGORY
    ]
    return render(request, "translations/hr_blocks.html", {
        "rows": rows, "missing": missing, "stale": stale, "category_navigation": category_navigation, "total_blocks": category_base.count(),
        "profession": profession, "category": category,
        "professions": HRTextBlock.objects.filter(active=True).exclude(profession="").order_by("profession").values_list("profession", flat=True).distinct(),
        "categories": HRTextBlock.CATEGORY,
        "visible_languages": visible_languages,
        "inactive_languages": inactive_languages,
        "show_inactive": show_inactive,
    })


@login_required
@require_http_methods(["POST"])
def autosave(request, app_label, model_name, pk):
    """Persist a single translation draft. Never silently approve or publish it."""
    if model_name not in ALLOWED_MODELS.get(app_label, set()):
        raise Http404
    ct = get_object_or_404(ContentType, app_label=app_label, model=model_name)
    model = ct.model_class()
    if model is None:
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    if not request.user.has_perm(f"{app_label}.change_{model_name}"):
        raise PermissionDenied
    language = request.POST.get("language", "")
    field_name = request.POST.get("field", "")
    if language not in {code for code, _ in LANGUAGES if code != "de"}:
        return JsonResponse({"ok": False, "message": "Ungültige Sprache"}, status=400)
    allowed = {field.name for field in fields_for(obj)}
    if field_name not in allowed:
        return JsonResponse({"ok": False, "message": "Ungültiges Textfeld"}, status=400)
    value = request.POST.get("text", "")
    if len(value) > 30000:
        return JsonResponse({"ok": False, "message": "Maximal 30.000 Zeichen"}, status=422)
    source_hash = fingerprint(getattr(obj, field_name))
    with transaction.atomic():
        existing, _ = ContentTranslation.objects.select_for_update().get_or_create(
            content_type=ct, object_id=obj.pk, language=language, field_name=field_name,
            defaults={"text": "", "status": "draft", "source_hash": source_hash})
        # Keep the audit and the translation update in the same transaction.
        old_text, old_status = existing.text, existing.status
        # A previous approved translation is preserved when no text has changed.
        if existing.text != value:
            existing.text = value
            existing.status = "review" if value.strip() else "draft"
            existing.source_hash = source_hash
            existing.updated_by = request.user
            existing.save(update_fields=["text", "status", "source_hash", "updated_by", "updated_at"])
        elif existing.source_hash != source_hash:
            # Do not approve an outdated translation just because autosave ran.
            if existing.status == "published":
                existing.status = "review"
                existing.save(update_fields=["status", "updated_at"])
        if app_label == "recruiting" and model_name == "vacancy":
            changes = []
            field_label = f"{language.upper()} · {field_name}"
            if old_text != existing.text:
                changes.append({"field": field_label, "old": old_text, "new": existing.text})
            if old_status != existing.status:
                changes.append({"field": f"{field_label} (Status)", "old": old_status, "new": existing.status})
            if changes:
                from recruiting.models import HREditLog
                HREditLog.objects.create(
                    vacancy=obj, user=request.user, action="translation",
                    detail=f"Sprachversion {language.upper()} automatisch gespeichert",
                    changes=changes,
                )
    from django.utils import timezone
    return JsonResponse({"ok": True, "saved_at": timezone.localtime().strftime("%H:%M:%S"),
                         "status": existing.status})
