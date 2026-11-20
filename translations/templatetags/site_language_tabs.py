from django import template
from translations.models import SiteLanguageSettings

register = template.Library()

@register.simple_tag
def active_site_languages():
    return SiteLanguageSettings.enabled()

@register.simple_tag
def inactive_site_language_names():
    enabled = set(SiteLanguageSettings.enabled())
    return [name for code, name in (("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")) if code not in enabled]
