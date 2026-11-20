from django import template
from translations.models import SiteLanguageSettings

register = template.Library()

@register.filter
def language_visible(code, show_inactive=False):
    return str(code).lower() in SiteLanguageSettings.enabled() or bool(show_inactive)


@register.inclusion_tag("messen/partials/inactive_language_hint.html", takes_context=True)
def vertrieb_inactive_hint(context):
    request = context.get("request")
    active = set(SiteLanguageSettings.enabled())
    names = (("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano"))
    inactive = [name for code, name in names if code not in active]
    query = request.GET.copy() if request is not None else None
    showing = bool(query and query.get("show_inactive") == "1")
    if query is not None:
        query["show_inactive"] = "0" if showing else "1"
    return {"inactive_languages": inactive, "show_inactive": showing, "toggle_query": query.urlencode() if query is not None else "show_inactive=1"}
