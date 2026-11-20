import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .forms import ApplicationForm
from .models import Vacancy, Application, ApplicationCertificate, HRTip, ApplicationDepartment, HRTextBlock, VacancyDepartment

log = logging.getLogger(__name__)

def careers(request):
    # One unified list prevents duplicate AUSBILDUNG headings when some
    # training positions are published and others remain unpublished.
    vacancies = Vacancy.objects.filter(published=True) | Vacancy.objects.filter(published=False, category="ausbildung")
    vacancies = vacancies.order_by("category", "sort_order", "id")
    return render(request, "recruiting/careers.html", {"vacancies": vacancies, "tips": HRTip.objects.filter(published=True)[:3]})

def job_detail(request, slug):
    vacancy = get_object_or_404(Vacancy, slug=slug, published=True)
    language = request.GET.get("lang", "de").lower()
    visible = vacancy.visible_languages or []
    from django.http import Http404
    if language not in visible:
        raise Http404("Diese Sprachversion ist nicht veröffentlicht")
    values = {name: getattr(vacancy, name, "") or "" for name in ("title", "introduction", "responsibilities", "hard_skills", "soft_skills", "requirements", "benefits")}
    if language != "de":
        from django.contrib.contenttypes.models import ContentType
        from translations.models import ContentTranslation
        from translations.services import fingerprint
        ct = ContentType.objects.get_for_model(vacancy)
        originals = dict(values)
        entries = ContentTranslation.objects.filter(content_type=ct, object_id=vacancy.pk, language=language, field_name__in=values.keys())
        for entry in entries:
            if entry.status == "published" and entry.text.strip() and entry.source_hash == fingerprint(values[entry.field_name]):
                values[entry.field_name] = entry.text
            else:
                # Avoid leaking a stale or unfinished translation as a published version.
                raise Http404("Sprachversion benötigt eine erneute Prüfung")
        if any(not entries.filter(field_name=name).exists() for name, value in originals.items() if value):
            raise Http404("Sprachversion ist unvollständig")
    return render(request, "recruiting/job.html", {"job": vacancy, "public_language": language, "public_values": values, "preview_values": values, "preview_language": language, "visible_languages": visible})

def tips(request):
    return render(request, "recruiting/tips.html", {"tips": HRTip.objects.filter(published=True)})

@require_http_methods(["GET", "POST"])
def apply(request, slug=None):
    vacancy = get_object_or_404(Vacancy, Q(published=True) | Q(category="ausbildung"), slug=slug) if slug else None
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, vacancy=vacancy)
        # A hidden honeypot rejects basic automated submissions.
        if request.POST.get("website", "").strip():
            return render(request, "recruiting/apply.html", {"form": ApplicationForm(vacancy=vacancy), "job": vacancy, "success": True})
        if not form.is_valid():
            log.warning("HR application form rejected: invalid fields=%s", list(form.errors.keys()))
        else:
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            for uploaded in form.cleaned_data.get("certificates_uploads", []):
                ApplicationCertificate.objects.create(application=application, file=uploaded)
            try:
                send_mail(
                    f"Neue HAMMEL Bewerbung: {vacancy.title if vacancy else 'Initiativbewerbung'}",
                    f"Neue Bewerbung im HR-Portal, Vorgang #{application.pk}.\nBitte im geschützten Django-Admin ansehen. Keine Bewerbungsunterlagen per E-Mail.",
                    settings.DEFAULT_FROM_EMAIL, [settings.HR_NOTIFICATION_EMAIL], fail_silently=False,
                )
                application.notification_sent = True
                application.save(update_fields=["notification_sent"])
            except Exception:
                log.exception("HR mail notification failed for application %s", application.pk)
            # Applicant acknowledgement is independent of the internal HR notification.
            # Never include submitted documents or sensitive application details in email.
            try:
                send_mail(
                    "HAMMEL | Eingangsbestätigung Ihrer Bewerbung",
                    (
                        f"Guten Tag {application.full_name},\n\n"
                        "vielen Dank für Ihr Interesse an HAMMEL Recyclingtechnik und "
                        "für Ihre Bewerbung.\n\n"
                        "Wir bestätigen Ihnen, dass Ihre Bewerbung und die über das "
                        "Bewerbungsformular eingereichten Unterlagen bei uns eingegangen sind. "
                        "Unser HR-Team wird Ihre Bewerbung prüfen und sich bei Ihnen melden, "
                        "sobald es Neuigkeiten gibt.\n\n"
                        "Bitte antworten Sie auf diese E-Mail, falls Sie Fragen zu Ihrer "
                        "Bewerbung haben.\n\n"
                        "Freundliche Grüße\n"
                        "Ihr HAMMEL HR-Team\n"
                        "HAMMEL Recyclingtechnik GmbH"
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [application.email],
                    fail_silently=False,
                )
            except Exception:
                log.exception("Applicant confirmation email failed for application %s", application.pk)
            return render(request, "recruiting/apply.html", {"success": True, "job": vacancy})
    else: form = ApplicationForm(vacancy=vacancy)
    return render(request, "recruiting/apply.html", {"form": form, "job": vacancy})

@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_management(request):
    return render(request, "recruiting/staff_panel.html", _hr_panel_context())


def _hr_panel_context(section=None):
    vacancies = list(Vacancy.objects.select_related("department").order_by("sort_order", "id"))
    job_departments = list(VacancyDepartment.objects.all())
    vacancy_groups = []
    for key, title in Vacancy.CATEGORY:
        items = [v for v in vacancies if v.category == key]
        if key == "job":
            subgroups = [
                {"key": str(d.pk), "title": d.name, "items": [v for v in items if v.department_id == d.pk]}
                for d in job_departments if d.active or any(v.department_id == d.pk for v in items)
            ]
            subgroups.append({"key": "unassigned", "title": "Ohne Abteilung", "items": [v for v in items if v.department_id is None]})
        else:
            subgroups = [{"key": key, "title": title, "items": items}]
        vacancy_groups.append({"key": key, "title": title, "items": items, "subgroups": subgroups})
    return {
        "section": section,
        "applications": Application.objects.select_related("vacancy")[:100],
        "vacancies": vacancies,
        "vacancy_groups": vacancy_groups,
        "job_departments": job_departments,
        "departments": ApplicationDepartment.objects.all(),
        "tips": HRTip.objects.all(),
        "new_count": Application.objects.filter(status="new").count(),
    }


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_dashboard(request):
    from translations.models import ContentTranslation
    from django.contrib.contenttypes.models import ContentType
    from translations.services import fingerprint, fields_for
    vacancies = list(Vacancy.objects.all())
    ct = ContentType.objects.get_for_model(Vacancy)
    translations = ContentTranslation.objects.filter(content_type=ct, object_id__in=[v.pk for v in vacancies]).only('object_id','language','field_name','text','status','source_hash')
    by_vacancy = {}
    for item in translations:
        by_vacancy.setdefault(item.object_id, []).append(item)
    pending_translation_ids = []
    for vacancy in vacancies:
        required = [(f.name, str(getattr(vacancy, f.name, '') or '')) for f in fields_for(vacancy)]
        required = [(name, value) for name, value in required if value.strip()]
        if any(not any(t.language == lang and t.field_name == name and t.text.strip() and t.status == 'published' and t.source_hash == fingerprint(value) for t in by_vacancy.get(vacancy.pk, [])) for lang in ('en','fr','es','it') for name,value in required):
            pending_translation_ids.append(vacancy.pk)
    return render(request, "recruiting/staff_home.html", {
        "pending_publication": Vacancy.objects.filter(published=False).count(),
        "pending_translations": len(pending_translation_ids),
        "pending_translation_vacancy": pending_translation_ids[0] if pending_translation_ids else None,
        "recent_drafts": list(Vacancy.objects.filter(published=False).order_by('-updated_at')[:4]),
        "vacancy_count": Vacancy.objects.count(),
        "department_count": ApplicationDepartment.objects.count(),
        "tip_count": HRTip.objects.count(),
        "new_count": Application.objects.filter(status="new").count(),
    })


@login_required(login_url="hr_login")
@permission_required("recruiting.change_vacancy", raise_exception=True)
@require_http_methods(["POST"])
def hr_autosave(request, pk):
    """Save only valid German draft fields. Never alter publication or translations."""
    from django import forms
    from django.db import models as db_models
    from django.db import transaction
    from django.utils import timezone
    obj = get_object_or_404(Vacancy, pk=pk)
    if obj.published:
        return JsonResponse({"ok": False, "message": "Veröffentlichte Stellen werden nicht automatisch überschrieben."}, status=409)
    fields = tuple(f for f in HR_EDITABLE['vacancy'][1] if f != 'published')
    Form = forms.modelform_factory(Vacancy, fields=fields)
    form = Form(request.POST, instance=obj)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors.get_json_data()}, status=422)
    with transaction.atomic():
        locked = Vacancy.objects.select_for_update().get(pk=pk)
        # Keep published flag, slug, order and all other server-owned fields intact.
        for name in fields:
            if name == 'department' and form.cleaned_data['category'] != 'job':
                setattr(locked, name, None)
            else:
                setattr(locked, name, form.cleaned_data[name])
        locked.save(update_fields=[*fields, 'updated_at'])
    return JsonResponse({'ok': True, 'saved_at': timezone.localtime().strftime('%H:%M:%S')})


@login_required(login_url="hr_login")
@permission_required("recruiting.view_vacancy", raise_exception=True)
def hr_preview(request, pk):
    """Use the actual public job template for unpublished staff preview."""
    vacancy = get_object_or_404(Vacancy, pk=pk)
    from django.contrib.contenttypes.models import ContentType
    from translations.models import ContentTranslation
    from translations.services import fingerprint, fields_for

    language = request.GET.get('lang', 'de').lower()
    if language not in {'de', 'en', 'fr', 'es', 'it'}:
        language = 'de'
    preview_fields = ('title', 'introduction', 'responsibilities', 'hard_skills', 'soft_skills', 'requirements', 'benefits')
    preview_values = {name: getattr(vacancy, name, '') or '' for name in preview_fields}
    missing_fields = []
    stale_fields = []
    preview_statuses = {}
    field_labels = {'title':'Stellenbezeichnung', 'introduction':'Einleitung', 'responsibilities':'Aufgaben', 'hard_skills':'Fachliche Kenntnisse', 'soft_skills':'Persönliche Stärken', 'requirements':'Weitere Anforderungen', 'benefits':'Das bieten wir dir'}
    if language != 'de':
        ct = ContentType.objects.get_for_model(vacancy)
        allowed = {f.name for f in fields_for(vacancy)}
        translations = {entry.field_name: entry for entry in ContentTranslation.objects.filter(
            content_type=ct, object_id=vacancy.pk, language=language, field_name__in=preview_fields
        )}
        for name in preview_fields:
            original = preview_values[name]
            if not original or name not in allowed:
                continue
            entry = translations.get(name)
            if not entry or not entry.text.strip() or entry.text.strip().casefold() in {'example', 'test', 'übersetzung fehlt'}:
                missing_fields.append(name)
                preview_statuses[name] = "missing"
                # Keep the German original visible in staff preview, clearly labelled as fallback.
                preview_values[name] = original
            else:
                preview_values[name] = entry.text
                if entry.source_hash != fingerprint(original):
                    stale_fields.append(name)
                    preview_statuses[name] = "review"
                else:
                    preview_statuses[name] = {"draft": "working", "review": "review", "published": "translated"}.get(entry.status, "working")
    response = render(request, 'recruiting/job.html', {
        'job': vacancy, 'staff_preview': True, 'preview_language': language,
        'preview_values': preview_values, 'preview_languages': [('de','Deutsch'),('en','English'),('fr','Français'),('es','Español'),('it','Italiano')], 'preview_missing': missing_fields,
        'preview_stale': stale_fields, 'preview_statuses': preview_statuses, 'preview_status_counts': {status: sum(value == status for value in preview_statuses.values()) for status in ('missing','working','review','translated')}, 'preview_missing_labels': [field_labels[n] for n in missing_fields], 'preview_stale_labels': [field_labels[n] for n in stale_fields],
    })
    response['Cache-Control'] = 'no-store, private'
    return response


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_section(request, section):
    if section not in ("stellen", "bereiche", "tipps", "bewerbungen"):
        from django.http import Http404
        raise Http404
    return render(request, "recruiting/staff_panel.html", _hr_panel_context(section))


HR_EDITABLE = {
    "vacancy": (Vacancy, ("title", "category", "department", "location", "employment_type", "introduction", "responsibilities", "requirements", "hard_skills", "soft_skills", "benefits", "published")),
    "job_department": (VacancyDepartment, ("name", "active", "sort_order")),
    "department": (ApplicationDepartment, ("name", "active", "sort_order")),
    "tip": (HRTip, ("title", "body", "order", "published")),
    "application": (Application, ("status", "notes")),
}


def _vacancy_edit_changes(form, instance, old_values):
    """Prepare the German-original audit diff without touching translations."""
    return [
        {
            "field": str(form.fields[name].label or name),
            "old": old_values.get(name, ""),
            "new": str(getattr(instance, name) or ""),
        }
        for name in form.changed_data
    ]


def _save_vacancy_new_blocks(raw_json, block_model):
    """Save only valid new draft text blocks; never modify existing library entries."""
    import json

    try:
        custom = json.loads(raw_json)
    except (ValueError, TypeError):
        return
    if not isinstance(custom, list):
        return
    for item in custom[:100]:
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        text = str(item.get("text", "")).strip()[:300]
        profession = str(item.get("profession", ""))[:40]
        if category in ("responsibilities", "hard_skills", "soft_skills", "benefits") and text:
            block_model.objects.get_or_create(
                category=category, text=text,
                defaults={"profession": profession, "active": False},
            )


def _vacancy_translation_summary(required, translations, languages, fingerprint):
    """Summarize translation readiness without modifying any database records."""
    summary = []
    for code, name in languages[1:]:
        entries = {item.field_name: item for item in translations if item.language == code}
        ready = review = missing = stale = 0
        for field, value in required:
            entry = entries.get(field)
            if not entry or not entry.text.strip() or entry.text.strip().casefold() in {'example', 'test', 'übersetzung fehlt'}:
                missing += 1
            elif entry.source_hash != fingerprint(value):
                stale += 1
            elif entry.status == "published":
                ready += 1
            else:
                review += 1
        summary.append({
            "code": code, "name": name, "ready": ready,
            "review": review, "missing": missing, "stale": stale,
            "total": len(required),
            "percent": round(100 * ready / len(required)) if required else 100,
            "complete": bool(required) and ready == len(required),
        })
    return summary


def _vacancy_publication_checks(vacancy):
    """Required public-facing German content, independent of translation readiness."""
    labels = {
        "title": "Stellenbezeichnung", "location": "Arbeitsort",
        "introduction": "Einleitung", "responsibilities": "Deine Aufgaben",
        "benefits": "Das bieten wir",
    }
    missing = [label for name, label in labels.items() if not str(getattr(vacancy, name, "") or "").strip()]
    if vacancy.category == "job" and not vacancy.department_id:
        missing.append("Abteilung")
    return missing


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
@require_http_methods(["GET", "POST"])
def hr_edit(request, kind, pk=None):
    from django import forms
    from django.db import models as db_models
    from django.contrib import messages
    from django.contrib.auth.decorators import permission_required
    from django.http import HttpResponseForbidden
    from django.urls import reverse
    if kind not in HR_EDITABLE:
        from django.http import Http404
        raise Http404
    model, fields = HR_EDITABLE[kind]
    if kind == "vacancy":
        fields = tuple(field for field in fields if field != "published")
    perm_action = "change" if pk else "add"
    if not request.user.has_perm(f"recruiting.{perm_action}_{model._meta.model_name}"):
        return HttpResponseForbidden("Keine Berechtigung")
    if kind == "application" and not pk:
        return HttpResponseForbidden("Bewerbungen können nicht manuell angelegt werden")
    obj = get_object_or_404(model, pk=pk) if pk else None
    if kind == "tip":
        from django.db import transaction
        from django.contrib.contenttypes.models import ContentType
        from translations.models import ContentTranslation
        from translations.services import fingerprint
        from translations.models import SiteLanguageSettings
        enabled_codes = set(SiteLanguageSettings.enabled())
        all_languages = (("de", "Deutsch"), ("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano"))
        show_inactive = request.GET.get("show_inactive") == "1"
        inactive_languages = tuple((code, label) for code, label in all_languages if code not in enabled_codes)
        languages = tuple((code, label) for code, label in all_languages if code in enabled_codes or show_inactive)
        ct = ContentType.objects.get_for_model(model)
        existing = {(entry.language, entry.field_name): entry for entry in ContentTranslation.objects.filter(
            content_type=ct, object_id=obj.pk, field_name__in=("title", "body"), language__in=("en", "fr", "es", "it"))} if obj else {}
        values = {(code, field): (getattr(obj, field) if obj else "") if code == "de" else
                  (existing[(code, field)].text if (code, field) in existing else "")
                  for code, _ in languages for field in ("title", "body")}
        published = obj.published if obj else False
        errors = []
        if request.method == "POST":
            values = {(code, field): request.POST.get(f"{field}_{code}", "").strip()
                      for code, _ in languages for field in ("title", "body")}
            published = request.POST.get("published") == "on"
            if not values[("de", "title")] or not values[("de", "body")]:
                errors.append("Deutscher Titel und deutscher Text sind erforderlich.")
            if any(len(values[(code, "title")]) > 140 for code, _ in languages):
                errors.append("Titel dürfen maximal 140 Zeichen enthalten.")
            if not errors:
                with transaction.atomic():
                    locked = model.objects.select_for_update().get(pk=obj.pk) if obj else model()
                    locked.title, locked.body = values[("de", "title")], values[("de", "body")]
                    locked.published = published
                    locked.save()
                    for code, _ in languages[1:]:
                        for field in ("title", "body"):
                            value, source_hash = values[(code, field)], fingerprint(values[("de", field)])
                            record = ContentTranslation.objects.select_for_update().filter(
                                content_type=ct, object_id=locked.pk, field_name=field, language=code).first()
                            if record:
                                if record.text != value or record.source_hash != source_hash:
                                    record.text, record.source_hash = value, source_hash
                                    record.status = "review" if value else "draft"
                                    record.updated_by = request.user
                                    record.save(update_fields=["text", "source_hash", "status", "updated_by", "updated_at"])
                            elif value:
                                ContentTranslation.objects.create(content_type=ct, object_id=locked.pk,
                                    field_name=field, language=code, text=value, source_hash=source_hash,
                                    status="review", updated_by=request.user)
                messages.success(request, "HR-Tipp und alle Sprachversionen gespeichert.")
                return redirect("hr_section", section="tipps")
        return render(request, "recruiting/tipp_multilingual.html", {
            "object": obj, "languages": [{"code": code, "label": label,
                "title": values[(code, "title")], "body": values[(code, "body")]} for code, label in languages],
            "published": published, "errors": errors,
            "inactive_languages": inactive_languages, "show_inactive": show_inactive,
        })
    if kind in ("department", "job_department"):
        from django.db import transaction
        from django.contrib.contenttypes.models import ContentType
        from translations.models import ContentTranslation
        from translations.services import fingerprint
        from django.core.exceptions import ValidationError
        from translations.models import SiteLanguageSettings
        enabled_codes = set(SiteLanguageSettings.enabled())
        all_languages = (("de", "Deutsch"), ("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano"))
        show_inactive = request.GET.get("show_inactive") == "1"
        inactive_languages = tuple((code, label) for code, label in all_languages if code not in enabled_codes)
        languages = tuple((code, label) for code, label in all_languages if code in enabled_codes or show_inactive)
        ct = ContentType.objects.get_for_model(model)
        existing = {item.language: item for item in ContentTranslation.objects.filter(
            content_type=ct, object_id=obj.pk, field_name="name", language__in=("en", "fr", "es", "it")
        )} if obj else {}
        values = {"de": obj.name if obj else ""}
        values.update({code: existing[code].text if code in existing else "" for code, _ in languages[1:]})
        active = obj.active if obj else True
        errors = []
        if request.method == "POST":
            values = {code: request.POST.get("name_" + code, "").strip() for code, _ in languages}
            active = request.POST.get("active") == "on"
            if not values["de"]:
                errors.append("Die deutsche Bezeichnung ist erforderlich.")
            if any(len(value) > 120 for value in values.values()):
                errors.append("Bezeichnungen dürfen maximal 120 Zeichen enthalten.")
            if model.objects.filter(name=values["de"]).exclude(pk=obj.pk if obj else None).exists():
                errors.append("Diese deutsche Bezeichnung ist bereits vorhanden.")
            if not errors:
                with transaction.atomic():
                    locked = model.objects.select_for_update().get(pk=obj.pk) if obj else model()
                    locked.name = values["de"]
                    locked.active = active
                    # Preserve sort_order internally; do not expose it in the editor.
                    locked.save()
                    for code, _ in languages[1:]:
                        value = values[code]
                        record = ContentTranslation.objects.select_for_update().filter(
                            content_type=ct, object_id=locked.pk, field_name="name", language=code
                        ).first()
                        if record:
                            if record.text != value or record.source_hash != fingerprint(values["de"]):
                                record.text = value
                                record.source_hash = fingerprint(values["de"])
                                record.status = "review" if value else "draft"
                                record.save(update_fields=["text", "source_hash", "status", "updated_at"])
                        elif value:
                            ContentTranslation.objects.create(content_type=ct, object_id=locked.pk,
                                field_name="name", language=code, text=value,
                                source_hash=fingerprint(values["de"]), status="review")
                messages.success(request, "Alle Sprachversionen gespeichert.")
                return redirect("hr_section", section="bereiche")
        return render(request, "recruiting/bereich_multilingual.html", {
            "object": obj, "kind": kind, "languages": [{"code": code, "label": label, "value": values[code]} for code, label in languages],
            "active": active, "errors": errors,
            "inactive_languages": inactive_languages, "show_inactive": show_inactive,
        })
    Form = forms.modelform_factory(model, fields=fields, widgets={
        f.name: forms.Textarea(attrs={"rows": 5}) for f in model._meta.fields if f.name in fields and isinstance(f, db_models.TextField)
    })
    # ModelForm.is_valid() mutates its bound instance during validation.
    # Snapshot the original database values before validation for a truthful audit.
    original_vacancy_values = (
        {name: str(getattr(obj, name) or "") for name in fields}
        if kind == "vacancy" and obj is not None and request.method == "POST"
        else {}
    )
    form = Form(request.POST or None, instance=obj)
    if kind == "vacancy" and obj is not None and request.GET.get("step") == "review":
        from translations.models import ContentTranslation, LANGUAGES
        from translations.services import fields_for
        from django.contrib.contenttypes.models import ContentType
        from translations.services import fingerprint
        content_type = ContentType.objects.get_for_model(obj)
        translations = ContentTranslation.objects.filter(content_type=content_type, object_id=obj.pk)
        required = [(field, str(getattr(obj, field, "") or "")) for field in (f.name for f in fields_for(obj))]
        required = [(field, value) for field, value in required if value.strip()]
        summary = _vacancy_translation_summary(required, translations, LANGUAGES, fingerprint)
        missing_german = _vacancy_publication_checks(obj)
        ready_languages = {"de"}
        for language_code in ("en", "fr", "es", "it"):
            records = {entry.field_name: entry for entry in translations if entry.language == language_code}
            if required and all(
                (entry := records.get(field)) is not None
                and entry.status == "published"
                and bool(entry.text.strip())
                and entry.source_hash == fingerprint(value)
                for field, value in required
            ):
                ready_languages.add(language_code)
        if request.method == "POST":
            if not request.user.has_perm("recruiting.change_vacancy"):
                return HttpResponseForbidden("Keine Berechtigung")
            action = request.POST.get("publication_action")
            if action == "languages":
                from .models import HREditLog
                from django.db import transaction
                allowed = {"de", "en", "fr", "es", "it"}
                selected = [code for code in ("de", "en", "fr", "es", "it") if code in request.POST.getlist("visible_languages")]
                with transaction.atomic():
                    locked = Vacancy.objects.select_for_update().get(pk=obj.pk)
                    invalid = [code for code in selected if code not in ready_languages]
                    if invalid:
                        messages.error(request, "Sprachversionen noch nicht vollständig geprüft: " + ", ".join(invalid))
                    else:
                        old = locked.visible_languages or []
                        locked.visible_languages = selected
                        locked.save(update_fields=["visible_languages"])
                        if old != selected:
                            HREditLog.objects.create(vacancy=locked, user=request.user, action="update", detail="Sprachsichtbarkeit geändert", changes=[{"field":"Sichtbare Sprachen", "old":", ".join(old), "new":", ".join(selected)}])
                        messages.success(request, "Sprachauswahl gespeichert.")
                return redirect(request.path + "?step=review")
            if action in ("publish", "unpublish"):
                if action == "publish" and missing_german:
                    messages.error(request, "Veröffentlichung nicht möglich: Bitte Pflichtangaben ergänzen.")
                elif request.POST.get("confirm_publication") != "yes":
                    messages.error(request, "Bitte bestätigen Sie die Statusänderung ausdrücklich.")
                else:
                    from django.db import transaction
                    from .models import HREditLog
                    with transaction.atomic():
                        locked = Vacancy.objects.select_for_update().get(pk=obj.pk)
                        if action == "publish" and _vacancy_publication_checks(locked):
                            messages.error(request, "Pflichtangaben wurden zwischenzeitlich geändert.")
                        else:
                            locked.published = action == "publish"
                            if action == "publish" and not locked.visible_languages:
                                locked.visible_languages = ["de"]
                            locked.save(update_fields=["published", "visible_languages"])
                            HREditLog.objects.create(vacancy=locked, user=request.user, action=action,
                                detail="Veröffentlichungsstatus bewusst geändert", changes=[{"field": "Veröffentlichung", "old": "Veröffentlicht" if obj.published else "Entwurf", "new": "Veröffentlicht" if locked.published else "Entwurf"}])
                            messages.success(request, "Veröffentlichungsstatus aktualisiert")
                return redirect(request.path + "?step=review")
        selected_month = request.GET.get("month", "")
        selected_year = request.GET.get("year", "")
        history = obj.edit_history.select_related("user")
        years = list(obj.edit_history.dates("created_at", "year", order="DESC").values_list("year", flat=True)) if False else [d.year for d in obj.edit_history.dates("created_at", "year", order="DESC")]
        if selected_month.isdigit() and 1 <= int(selected_month) <= 12:
            history = history.filter(created_at__month=int(selected_month))
        if selected_year.isdigit() and 2000 <= int(selected_year) <= 2100:
            history = history.filter(created_at__year=int(selected_year))
        history = history[:200]
        return render(request, "recruiting/staff_review.html", {
            "object": obj, "summary": summary, "missing_german": missing_german,
            "language_visibility": [{"code": code, "name": name, "ready": code in ready_languages, "visible": code in (obj.visible_languages or (["de"] if not obj.published else []))} for code, name in (("de","Deutsch"),("en","English"),("fr","Français"),("es","Español"),("it","Italiano"))],
            "translation_url": reverse("translation_edit", args=[obj._meta.app_label, obj._meta.model_name, obj.pk]),
            "history": history,
            "months": [{"value": str(i), "label": name} for i, name in enumerate(("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"), 1)],
            "years": years, "selected_month": selected_month, "selected_year": selected_year,
        })
    if kind == "vacancy":
        form.fields["department"].queryset = VacancyDepartment.objects.filter(active=True) | VacancyDepartment.objects.filter(pk=obj.department_id if obj else None)
        form.fields["department"].label = "Abteilung (nur bei Stellenangeboten)"
        form.fields["department"].help_text = "Für Ausbildung, Praktikum und Werkstudent nicht erforderlich."
        form.fields["requirements"].label = "Weitere Anforderungen / Sonstiges"
        form.fields["responsibilities"].label = "Deine Aufgaben"
        form.fields["hard_skills"].label = "Fachliche Kenntnisse (Hard Skills)"
        form.fields["soft_skills"].label = "Persönliche Stärken (Soft Skills)"
        form.fields["benefits"].label = "Das bieten wir"
    # Einheitliche deutsche Feldbezeichnungen im gesamten HR-Editor.
    hr_labels = {
        "title": "Stellenbezeichnung" if kind == "vacancy" else "Bezeichnung",
        "category": "Art der Stelle", "department": "Abteilung" if kind == "vacancy" else "Bereich",
        "location": "Arbeitsort", "employment_type": "Beschäftigungsart",
        "introduction": "Einleitung", "responsibilities": "Deine Aufgaben",
        "requirements": "Weitere Anforderungen / Sonstiges",
        "hard_skills": "Fachliche Kenntnisse", "soft_skills": "Persönliche Stärken",
        "benefits": "Das bieten wir", "published": "Veröffentlichen",
        "name": "Name", "active": "Aktiv", "sort_order": "Reihenfolge",
        "body": "Beschreibung", "order": "Reihenfolge", "status": "Bearbeitungsstatus",
        "notes": "Interne Notizen",
    }
    for field_name, label in hr_labels.items():
        if field_name in form.fields:
            form.fields[field_name].label = label
    if request.method == "POST" and form.is_valid():
        old_values = {name: original_vacancy_values.get(name, "") for name in form.changed_data} if kind == "vacancy" and obj else {}
        instance = form.save(commit=False)
        if kind == "vacancy" and instance.category != "job":
            instance.department = None
        instance.save()
        if kind == "vacancy":
            from .models import HREditLog
            HREditLog.objects.create(vacancy=instance, user=request.user, action="updated" if obj else "created", detail="Deutsche Originalfassung gespeichert", changes=_vacancy_edit_changes(form, instance, old_values))
        if kind == "vacancy":
            from translations.services import fill_vacancy_from_library
            fill_vacancy_from_library(instance)
        if kind != "application":
            from translations.services import save_inline
            save_inline(request, instance, form)
        if kind == "vacancy" and request.POST.get("save_new_blocks") == "1":
            _save_vacancy_new_blocks(request.POST.get("hr_new_blocks", "[]"), HRTextBlock)
        messages.success(request, "Deutsche Originalfassung gespeichert. Jetzt können Sie die Sprachversionen bearbeiten.")
        if kind == "vacancy":
            return redirect("translation_edit", app_label=instance._meta.app_label,
                            model_name=instance._meta.model_name, pk=instance.pk)
        if kind in ("tip", "department", "job_department"):
            return redirect("translation_edit", app_label=instance._meta.app_label,
                            model_name=instance._meta.model_name, pk=instance.pk)
        return redirect("hr_dashboard")
    blocks = list(HRTextBlock.objects.filter(active=True).values("category", "text", "profession")) if kind == "vacancy" else []
    return render(request, "recruiting/staff_edit.html", {"form": form, "kind": kind, "object": obj, "text_blocks": blocks, "translation_url": reverse("translation_edit", args=[obj._meta.app_label, obj._meta.model_name, obj.pk]) if obj and kind != "application" else None, "builder_fields": ("responsibilities", "hard_skills", "soft_skills", "benefits"), "multilingual": kind in ("tip", "department", "job_department")})


@login_required
@require_http_methods(["POST"])
@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
@require_http_methods(["POST"])
def hr_delete(request, kind, pk):
    from django.http import Http404, HttpResponseForbidden
    from django.contrib import messages
    if kind not in ("vacancy", "department", "job_department", "tip"):
        raise Http404
    model, _ = HR_EDITABLE[kind]
    if not request.user.has_perm(f"recruiting.delete_{model._meta.model_name}"):
        return HttpResponseForbidden("Keine Berechtigung")
    get_object_or_404(model, pk=pk).delete()
    messages.success(request, "Eintrag gelöscht")
    return redirect("hr_dashboard")


class HRLoginView(LoginView):
    template_name = "recruiting/hr_login.html"
    redirect_authenticated_user = False

    def get_success_url(self):
        return str(reverse_lazy("hr_dashboard"))

    def form_valid(self, form):
        if not form.get_user().has_perm("recruiting.view_application"):
            form.add_error(None, "Ihr Benutzerkonto hat keinen Zugang zum HR-Portal.")
            return self.form_invalid(form)
        return super().form_valid(form)


class HRLogoutView(LogoutView):
    next_page = reverse_lazy("hr_login")


def _reorder_hr_items(request, model, order_field, changed_message, allow_empty):
    """Validate and atomically save the complete order of HR items."""
    import json
    from django.db import transaction

    try:
        ids = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Ungültige JSON-Daten"}, status=400)

    valid = (
        isinstance(ids, list)
        and (allow_empty or bool(ids))
        and all(type(pk) is int and pk > 0 for pk in ids)
        and len(ids) == len(set(ids))
    )
    if not valid:
        return JsonResponse({"ok": False, "error": "Ungültige Reihenfolge"}, status=400)

    with transaction.atomic():
        current = set(model.objects.select_for_update().values_list("pk", flat=True))
        if set(ids) != current:
            return JsonResponse({"ok": False, "error": changed_message}, status=409)
        for position, pk in enumerate(ids, 1):
            model.objects.filter(pk=pk).update(**{order_field: position})

    saved = list(model.objects.order_by(order_field, "pk").values_list("pk", flat=True))
    if saved != ids:
        return JsonResponse(
            {"ok": False, "error": "Gespeicherte Reihenfolge stimmt nicht überein"},
            status=500,
        )
    return JsonResponse({"ok": True, "ids": saved})


@login_required(login_url="hr_login")
@permission_required("recruiting.change_hrtip", raise_exception=True)
@require_http_methods(["POST"])
def hr_reorder_tips(request):
    """Atomically reorder existing HR tips, preserving their content and status."""
    return _reorder_hr_items(
        request, HRTip, "order", "Tipps wurden geändert. Bitte Seite neu laden.",
        allow_empty=True,
    )


@login_required(login_url="hr_login")
@permission_required("recruiting.change_applicationdepartment", raise_exception=True)
@require_http_methods(["POST"])
def hr_reorder_departments(request):
    """Save the complete department order in one atomic operation."""
    return _reorder_hr_items(
        request, ApplicationDepartment, "sort_order",
        "Bereiche wurden geändert. Bitte Seite neu laden.",
        allow_empty=False,
    )


@login_required(login_url="hr_login")
@permission_required("recruiting.change_vacancy", raise_exception=True)
@require_http_methods(["POST"])
def hr_reorder_vacancies(request):
    """Save the complete, validated drag order; no partial or cross-user updates."""
    import json
    from django.db import transaction
    from django.http import JsonResponse
    try:
        ids = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Ungültige Daten"}, status=400)
    if not isinstance(ids, list) or any(type(i) is not int or i <= 0 for i in ids) or len(ids) != len(set(ids)):
        return JsonResponse({"ok": False, "error": "Ungültige Reihenfolge"}, status=400)
    with transaction.atomic():
        vacancies = list(Vacancy.objects.select_for_update().all())
        if set(ids) != {v.pk for v in vacancies}:
            return JsonResponse({"ok": False, "error": "Die Stellenliste wurde geändert. Bitte neu laden."}, status=409)
        # A drag operation may reorder vacancies only within their own category.
        # Order must stay within the original category and department.
        def group(v):
            return (v.category, v.department_id if v.category == "job" else None)
        expected = {}
        for category, _ in Vacancy.CATEGORY:
            if category == "job":
                for department in VacancyDepartment.objects.all():
                    for v in vacancies:
                        if group(v) == ("job", department.pk):
                            expected.setdefault(group(v), []).append(v.pk)
                for v in vacancies:
                    if group(v) == ("job", None):
                        expected.setdefault(group(v), []).append(v.pk)
            else:
                for v in vacancies:
                    if v.category == category:
                        expected.setdefault(group(v), []).append(v.pk)
        received = {}
        by_id = {v.pk: v for v in vacancies}
        for pk in ids:
            received.setdefault(group(by_id[pk]), []).append(pk)
        if list(received) != list(expected):
            return JsonResponse({"ok": False, "error": "Verschieben zwischen Gruppen ist nicht erlaubt."}, status=400)
        for pos, pk in enumerate(ids, start=1):
            Vacancy.objects.filter(pk=pk).update(sort_order=pos*10)
    return JsonResponse({"ok": True})


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_application_detail(request, pk):
    from django.contrib import messages
    application = get_object_or_404(Application.objects.select_related("vacancy"), pk=pk)
    if request.method == "POST":
        if not request.user.has_perm("recruiting.change_application"):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        allowed = dict(Application.STATUS)
        status = request.POST.get("status", "")
        if status not in allowed:
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Ungültiger Status")
        application.status = status
        application.notes = request.POST.get("notes", "")[:20000]
        application.save(update_fields=["status", "notes"])
        messages.success(request, "Bewerbung wurde gespeichert")
        return redirect("hr_application_detail", pk=pk)
    return render(request, "recruiting/staff_application_detail.html", {"application": application})


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_application_document(request, pk, kind, certificate_id=None):
    from django.http import FileResponse, Http404
    from django.utils.text import get_valid_filename
    import os
    application = get_object_or_404(Application, pk=pk)
    if kind == "cv":
        field = application.cv
    elif kind == "cover":
        field = application.cover_letter
    elif kind == "certificate":
        if certificate_id is None:
            field = application.certificates
        else:
            certificate = get_object_or_404(ApplicationCertificate, pk=certificate_id, application=application)
            field = certificate.file
    else:
        raise Http404
    if not field:
        raise Http404
    try:
        handle = field.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404
    response = FileResponse(handle, as_attachment=True, filename=get_valid_filename(os.path.basename(field.name)))
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
