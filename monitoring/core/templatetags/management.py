from django import template


register = template.Library()


def bytes_to_mbi(value):
    return round(value / (1024 * 1024), 2)


register.filter("bytes_to_mbi", bytes_to_mbi)
