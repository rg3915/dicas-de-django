# 34 - Django: custom template tags

<a href="https://youtu.be/ldMf8AW2h4Y">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://docs.djangoproject.com/en/3.2/ref/templates/builtins/

### Built-in tags

```html
{% for obj in object_list %}
  <tr>
    <td>{{ forloop.counter }}</td>
    ...
    {% if obj.category.title == 'Django' %}
      <td>{{ obj.category }}</td>
    {% endif %}
  </tr>
{% endfor %}
```


### Built-in filter

```html
...
<td>{{ forloop.counter }}</td>
<td>{{ obj.title|slugify }}</td>
<td>{{ obj.title|truncatechars:13 }}</td>
<td>{{ obj.subtitle|safe|default:"---" }}</td>
<td>{{ obj.published_date|date:"d/m/Y" }}</td>
...
```

```
subtitle='<p>lorem</p>'
```


```html
{{ obj.subtitle|safe }}
```

### Writing custom template filters

#### Code layout

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout

```
core
├── __init__.py
├── models.py
├── templatetags
│   ├── __init__.py
│   ├── model_name_tags.py
│   └── usergroup_tags.py
```

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters

```
mkdir myproject/core/templatetags
touch myproject/core/templatetags/__init__.py
touch myproject/core/templatetags/usergroup_tags.py
```


```python
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
```

```html
{% load usergroup_tags %}

{% if request.user|has_group:"Autor" %}
É Autor.
{% endif %}
```

### Writing custom template tags

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-tags

```
touch myproject/core/templatetags/model_name_tags.py
```

```python
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
```

```html
{% load model_name_tags %}

Lista de {% model_name_plural model %}
```
