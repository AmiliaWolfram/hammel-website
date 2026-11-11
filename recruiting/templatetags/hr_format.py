from django import template
register = template.Library()
@register.filter
def hr_lines(value):
    return [line.strip().lstrip("•-– ").strip() for line in (value or "").splitlines() if line.strip().lstrip("•-– ").strip()]

@register.filter
def preview_status(mapping, key):
    return mapping.get(key, "") if isinstance(mapping, dict) else ""
