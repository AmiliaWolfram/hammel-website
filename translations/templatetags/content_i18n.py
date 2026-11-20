from django import template
from translations.services import translated
register = template.Library()
@register.simple_tag(takes_context=True)
def translated_field(context, obj, field):
    request = context.get("request")
    lang = getattr(request, "LANGUAGE_CODE", "de") if request else "de"
    return translated(obj, field, lang[:2])


@register.inclusion_tag("translations/inline.html", takes_context=True)
def inline_translations(context, obj, form=None):
    from translations.services import inline_payload
    from translations.models import SiteLanguageSettings, LANGUAGES
    # Context-aware inclusion tag: contact editor uses a full-width language grid.
    return {"inline": inline_payload(obj, form), "portal": "hr" if obj is not None and obj._meta.app_label == "recruiting" else "vertrieb",
            "contact_mode": bool(obj is not None and obj._meta.app_label == "contacts"),
            "machine_product_mode": bool(obj is not None and obj._meta.app_label == "messen" and obj._meta.model_name == "machineproduct"),
            "show_inactive": context.get("request").GET.get("show_inactive") == "1" if context.get("request") else False,
            "active_languages": [(code, label) for code, label in LANGUAGES if code != "de" and code in SiteLanguageSettings.enabled()],
            "inactive_languages": [(code, label) for code, label in LANGUAGES if code != "de" and code not in SiteLanguageSettings.enabled()]}
