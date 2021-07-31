# 38 - Django: Paginação + Filtros

<a href="https://youtu.be/eXipSfa-HOQ">
    <img src="../.gitbook/assets/youtube.png">
</a>


Primeiro vamos definir a paginação:

Edite `views.py`

```python
# views.py
class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5
```

Edite `person_list.html`

```html
<!-- person_list.html -->
...
{% include "includes/pagination.html" %}
```

Criar `includes/pagination.html`

```
mkdir myproject/core/templates/includes
touch myproject/core/templates/includes/pagination.html
```


```html
<!-- pagination.html -->
<!-- https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b -->
<!-- Use https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b#file-pagination02-html -->
<div class="row text-center">
  <div class="col-lg-12">
    <ul class="pagination">
      {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">&laquo;</a></li>
      {% endif %}

      {% for pg in page_obj.paginator.page_range %}
        <!-- Sempre mostra as 3 primeiras e 3 últimas páginas -->
          {% if pg == 1 or pg == 2 or pg == 3 or pg == page_obj.paginator.num_pages or pg == page_obj.paginator.num_pages|add:'-1' or pg == page_obj.paginator.num_pages|add:'-2' %}
            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% else %}
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% endif %}

          {% else %}

            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg > page_obj.number|add:'-4' and pg < page_obj.number|add:'4' %} <!-- Mostra 3 páginas antes e 3 páginas depois da atual -->
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
              <li class="page-item"><a class="page-link" href="">...</a></li>
            {% endif %}
          {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
          <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">&raquo;</a></li>
        {% endif %}
    </ul>
  </div>
</div>
```

Editar novamente `views.py`

```python
# views.py
from django.db.models import Q


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PersonListView, self).get_queryset()

        data = self.request.GET
        search = data.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(bio__icontains=search)
            )

        return queryset
```

Criar templatetags `url_replace.py`

```
touch myproject/core/templatetags/url_replace.py
```

```python
# url_replace.py
# https://stackoverflow.com/a/62587351/802542
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.update(kwargs)
    return query.urlencode()
```

E finalmente edite `pagination.html` trocando todos os `href`

```html
<!-- pagination.html -->
{% load url_replace %}
...
href="?{% url_replace page=page_obj.previous_page_number %}"
...
href="?{% url_replace page=pg %}"
...
href="?{% url_replace page=page_obj.next_page_number %}"
```
