from django.conf import settings
from django import template


register = template.Library()


@register.filter
def bytes_to_mbi(value):
    return round(value / (1024 * 1024), 2)


@register.simple_tag
def admin_theme():
    return settings.THEME
