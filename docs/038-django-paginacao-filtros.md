# Dica 38 - Django: Paginação + Filtros

**Versões usadas no vídeo:** Django 2.2, Python 3.8 e Bootstrap 4.
{: .versoes }

<a href="https://youtu.be/eXipSfa-HOQ">
    <img src="../.gitbook/assets/youtube.png">
</a>


**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)


Gist da paginação: [https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b](https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b)

Paginar uma lista no Django é fácil: basta um `paginate_by` na `ListView`. O problema aparece quando a lista também tem uma busca. Você busca por "an", vai para a página 2 e... o filtro some, porque o link da página é só `?page=2`. Neste tutorial vamos:

1. paginar a lista de pessoas;
2. fazer o campo de busca funcionar;
3. criar uma template tag `url_replace` que monta os links da paginação **mantendo** os outros parâmetros da URL (o filtro).

## Pré-requisitos

Continuamos o projeto da [Dica 37 - Faker](037-faker.md): a app `myproject/core` tem o modelo `Person` (`first_name`, `last_name`, `email`, `bio`, `birthday`), uma `PersonListView` em `/persons/`, o template `core/person_list.html` com um formulário de busca (um `<input name="search">`) e uma tabela, e o comando `create_data` que cadastrou 100 pessoas com o Faker. A pasta `myproject/core/templatetags` (com o `__init__.py`) já existe desde a [Dica 34 - Custom template tags](034-django-custom-template-tags.md).

## Passo 1: paginando a ListView

Em `views.py`, acrescente `paginate_by` na `PersonListView`. O valor 5 é pequeno de propósito, para termos muitas páginas:

```python
# myproject/core/views.py
class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5
```

Com isso a página passa a mostrar só 5 pessoas, e a `ListView` coloca no contexto, além do `object_list` (agora só com os itens da página), o `page_obj` (a página atual), o `paginator` e o `is_paginated`. A página é escolhida pelo parâmetro `?page=` da URL.

## Passo 2: o template da paginação

Falta mostrar os links das páginas. Crie uma pasta `includes` dentro de `templates` e o arquivo `pagination.html`:

```bash
mkdir myproject/core/templates/includes
touch myproject/core/templates/includes/pagination.html
```

No final de `person_list.html`, logo depois da tabela, inclua a paginação:

```html
<!-- myproject/core/templates/core/person_list.html -->
...
  </table>

  {% include "includes/pagination.html" %}
{% endblock content %}
```

No vídeo, o rodapé do `base.html` foi desativado (comentado), porque atrapalhava a visualização da paginação:

```html
<!-- myproject/core/templates/base.html -->
...
  <!-- { include "footer.html" %} -->
...
```

Agora o `pagination.html`, baseado no gist de paginação (ele usa as classes de paginação do Bootstrap 4). Esta é a primeira versão, ainda com os links simples `?page=`:

```html
<!-- myproject/core/templates/includes/pagination.html -->
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

Como funciona:

* `&laquo;` («) aparece se existe página anterior (`has_previous`) e leva para `previous_page_number`; `&raquo;` (») é o equivalente para a próxima página.
* O `for` percorre todas as páginas (`page_range`), mas não mostra todas. O primeiro `if` sempre mostra as 3 primeiras e as 3 últimas páginas. Como o Django não tem subtração no template, `num_pages|add:'-1'` faz o papel de `num_pages - 1`.
* Para as páginas do meio, mostra só as que estão até 3 posições antes ou depois da página atual (`pg > number - 4 and pg < number + 4`), e coloca reticências (`...`) na 4ª posição de cada lado, indicando que há páginas escondidas.
* A página atual recebe a classe `active` do Bootstrap, que a destaca.

Rode o servidor e acesse `/persons/`: aparecem as 5 primeiras pessoas e, embaixo, `1 2 3 4 ... 18 19 20 »` (com 100 pessoas e 5 por página são 20 páginas).

## Passo 3: fazendo a busca funcionar

O formulário da lista envia o termo digitado no parâmetro `search` (é o `name` do `<input>`), pelo método GET: `/persons/?search=an`. Na view, sobrescreva o `get_queryset` para filtrar pelo termo:

```python
# myproject/core/views.py
from django.db.models import Q
from django.views.generic import ListView

from .models import Person


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

* `super().get_queryset()` devolve o queryset padrão da `ListView` (`Person.objects.all()`).
* `self.request.GET` é o dicionário com os parâmetros da URL; `data.get('search')` devolve `None` se o parâmetro não existir, então o filtro só é aplicado quando há algo digitado.
* Os objetos `Q` unidos com `|` formam um **OU**: a pessoa entra no resultado se o termo aparecer no nome, no sobrenome, no e-mail **ou** na biografia. O `icontains` busca o termo em qualquer parte do texto, sem diferenciar maiúsculas de minúsculas.

Busque por `an`: a lista é filtrada e paginada. Mas clique na página 2 e veja a URL: `/persons/?page=2`. O `search=an` sumiu e a lista voltou a mostrar todo mundo. É isso que vamos resolver agora.

## Passo 4: a template tag url_replace

Precisamos de links que mantenham todos os parâmetros atuais da URL e troquem só o `page`. Crie a template tag:

```bash
touch myproject/core/templatetags/url_replace.py
```

```python
# myproject/core/templatetags/url_replace.py
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

Linha a linha:

* `@register.simple_tag(takes_context=True)`: registra uma *simple tag* que recebe o contexto do template como primeiro argumento. É pelo contexto que pegamos o `request` (o context processor `django.template.context_processors.request` precisa estar ativo em `TEMPLATES`, o que é o padrão do `startproject`).
* `context['request'].GET.copy()`: o `request.GET` é um `QueryDict` imutável; o `copy()` devolve uma cópia que podemos alterar.
* `query.pop('page', None)`: tira o `page` atual, se houver.
* `query.update(kwargs)`: acrescenta os argumentos passados na tag, por exemplo `page=3`.
* `query.urlencode()`: devolve tudo como texto de URL, por exemplo `search=an&page=3`.

## Passo 5: usando a url_replace na paginação

Em `pagination.html`, carregue a tag no topo e troque todos os `href="?page=..."` por `href="?{% url_replace page=... %}"`. O arquivo final fica assim:

```html
<!-- myproject/core/templates/includes/pagination.html -->
{% load url_replace %}
<!-- https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b -->
<!-- Use https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b#file-pagination02-html -->
<div class="row text-center">
  <div class="col-lg-12">
    <ul class="pagination">
      {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?{% url_replace page=page_obj.previous_page_number %}">&laquo;</a></li>
      {% endif %}

      {% for pg in page_obj.paginator.page_range %}
        <!-- Sempre mostra as 3 primeiras e 3 últimas páginas -->
          {% if pg == 1 or pg == 2 or pg == 3 or pg == page_obj.paginator.num_pages or pg == page_obj.paginator.num_pages|add:'-1' or pg == page_obj.paginator.num_pages|add:'-2' %}
            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?{% url_replace page=pg %}">{{ pg }}</a></li>
            {% else %}
              <li class="page-item"><a class="page-link" href="?{% url_replace page=pg %}">{{ pg }}</a></li>
            {% endif %}

          {% else %}

            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?{% url_replace page=pg %}">{{ pg }}</a></li>
            {% elif pg > page_obj.number|add:'-4' and pg < page_obj.number|add:'4' %} <!-- Mostra 3 páginas antes e 3 páginas depois da atual -->
              <li class="page-item"><a class="page-link" href="?{% url_replace page=pg %}">{{ pg }}</a></li>
            {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
              <li class="page-item"><a class="page-link" href="">...</a></li>
            {% endif %}
          {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
          <li class="page-item"><a class="page-link" href="?{% url_replace page=page_obj.next_page_number %}">&raquo;</a></li>
        {% endif %}
    </ul>
  </div>
</div>
```

Note que o nome da biblioteca no `{% load %}` é o nome do arquivo (`url_replace.py`), e o nome da tag é o nome da função (`url_replace`). Depois de criar um arquivo novo em `templatetags`, reinicie o `runserver`.

## Testando

Rode o servidor:

```bash
python manage.py runserver
```

Acesse `/persons/`, digite `an` na busca e clique em OK. A URL fica `/persons/?search=an` e, no vídeo, a busca retornou 16 páginas. Agora os links da paginação levam o filtro junto:

```
/persons/?search=an&page=2
/persons/?search=an&page=3
...
/persons/?search=an&page=16
```

Você navega pela página 2, 3, até a última, e o filtro continua aplicado em todas.

## Conclusão

A paginação em si é só o `paginate_by`; o detalhe que costuma dar trabalho é preservar os outros parâmetros da URL. A `url_replace` resolve isso de forma genérica: ela funciona com qualquer filtro (busca, datas, categorias), porque copia todos os parâmetros do `request.GET` e troca só a página. No [gist](https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b) há outras variações do template de paginação.
