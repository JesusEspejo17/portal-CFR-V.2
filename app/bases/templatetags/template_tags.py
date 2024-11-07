from django import template

register = template.Library()

@register.filter(name='replace_underscore')
def replace_underscore(value):
    if isinstance(value, str):
        return value.replace('_', ' ')
    return value