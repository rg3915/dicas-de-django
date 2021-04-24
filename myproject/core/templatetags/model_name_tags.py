# model_name_tags.py
from django import template

register = template.Library()


@register.simple_tag
def model_name(value):
    '''
    Django template filter which returns the verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name.title()


@register.simple_tag
def model_name_plural(value):
    '''
    Django template filter which returns the plural verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name_plural.title()
