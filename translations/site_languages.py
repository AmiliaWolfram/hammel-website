from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .models import LANGUAGES, SiteLanguageSettings

@login_required
@require_http_methods(["GET", "POST"])
def settings_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Nur Administratoren dürfen Website-Sprachen verwalten.")
    if request.method == "POST":
        selected = [code for code, _ in LANGUAGES if code != "de" and code in request.POST.getlist("languages")]
        row, _ = SiteLanguageSettings.objects.get_or_create(pk=1, defaults={"enabled_languages": ["en", "fr", "es", "it"]})
        previous = set(row.enabled_languages)
        row.enabled_languages = selected
        row.save(update_fields=["enabled_languages", "updated_at"])
        activated = [code.upper() for code in selected if code not in previous]
        messages.success(request, "Sprachen gespeichert." + (" Neu aktiviert: " + ", ".join(activated) + ". Bitte fehlende Übersetzungen in HRPortal und Vertriebsportal vervollständigen." if activated else ""))
        return redirect("site_language_settings")
    active = SiteLanguageSettings.enabled()
    return render(request, "translations/site_language_settings.html", {"languages": [(code, name, code in active) for code, name in LANGUAGES], "active": active})
