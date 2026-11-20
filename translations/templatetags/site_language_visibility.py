from django import template
from translations.models import SiteLanguageSettings

register = template.Library()

@register.filter
def language_visible(code, show_inactive=False):
    return str(code).lower() in SiteLanguageSettings.enabled() or bool(show_inactive)
