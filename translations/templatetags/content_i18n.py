from django import template
from translations.services import translated
register = template.Library()
@register.simple_tag(takes_context=True)
def translated_field(context, obj, field):
    request = context.get("request")
    lang = getattr(request, "LANGUAGE_CODE", "de") if request else "de"
    return translated(obj, field, lang[:2])


@register.inclusion_tag("translations/inline.html")
def inline_translations(obj, form=None):
    from translations.services import inline_payload
    return {"inline": inline_payload(obj, form), "portal": "hr" if obj is not None and obj._meta.app_label == "recruiting" else "vertrieb"}
