# usergroup_tags.py
from django import template

register = template.Library()


@register.filter('name_group')
def name_group(user):
    ''' Retorna o nome do grupo do usuário. '''
    _groups = user.groups.first()
    if _groups:
        return _groups.name
    return ''


@register.filter('has_group')
def has_group(user, group_name):
    ''' Verifica se este usuário pertence a um grupo. '''
    if user:
        groups = user.groups.all().values_list('name', flat=True)
        return True if group_name in groups else False
    return False
