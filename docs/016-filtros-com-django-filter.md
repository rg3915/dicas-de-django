# Dica 16 - Filtros com django-filter

**Versões usadas no vídeo:** Django 2.2.13, django-filter 2.3.0, Python 3.8 e Bootstrap 4.0.
{: .versoes }

<a href="https://youtu.be/LZJjSeJC09A">
    <img src="../.gitbook/assets/youtube.png">
</a>


**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Na [Dica 15](015-busca-por-data-no-frontend.md) fizemos um filtro na mão: pegamos os valores do `request.GET` e montamos o `filter()` na view. Funciona, mas cada campo novo é mais código para escrever. O [django-filter](https://django-filter.readthedocs.io/en/stable/) é uma biblioteca que facilita bastante o uso de filtros na aplicação: você declara quais campos quer filtrar e ele gera o formulário e o queryset filtrado.

Neste tutorial vamos criar uma página "Artigos com filtros" que busca artigos pelo título e pelo sub-título, com o termo em qualquer parte do texto e sem diferenciar maiúsculas de minúsculas.

## Pré-requisitos

O projeto das dicas anteriores (repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django)), com o app `core` dentro de `myproject`, o `base.html` com Bootstrap 4 da [Dica 14](014-heranca-de-templates-e-arquivos-estaticos.md) e o modelo `Article`:

```python
# myproject/core/models.py
class Article(models.Model):
    id = HashidAutoField(primary_key=True)
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title
```

Os artigos cadastrados no vídeo são "Dicas de Python", "Dicas de Python 2", "Django Admin", "Django Autoslug", "Django Boilerplate" e "Django extensions" (o sub-título de cada um é igual ao título).

## Instalação

Instale o [django-filter](https://django-filter.readthedocs.io/en/stable/)

```
pip install django-filter
```

No vídeo, a versão instalada foi a 2.3.0 (com Django 2.2.13). Para fixar essa versão no `requirements.txt`:

```
django-filter==2.3.0
```

Acrescente-o ao `INSTALLED_APPS`. Repare que o nome do pacote no `pip` é `django-filter`, mas o nome do app é `django_filters`, no plural e com underline:

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'django_extensions',
    'daterange_filter',
    'django_filters',
    'myproject.core'
]
```

## O FilterSet

Na pasta do app, crie o arquivo `filters.py`:

```bash
cd myproject/core
touch filters.py
```

```python
# myproject/core/filters.py
import django_filters
from .models import Article


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    subtitle = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ('title', 'subtitle')
```

* Um `FilterSet` funciona parecido com um `ModelForm`: no `Meta` dizemos o modelo e os campos que podem ser filtrados.
* Por padrão, cada campo do `Meta.fields` é filtrado com o lookup `exact` (igualdade). Como queremos buscar uma parte do texto, declaramos os campos explicitamente como `CharFilter` com `lookup_expr='icontains'`. Algumas opções de lookup são `exact`, `iexact`, `contains` e `icontains`; o `i` significa que não diferencia maiúsculas de minúsculas, então `django` encontra "Django Admin".

## A view

Para não misturar com a view de artigos da Dica 15, criamos uma view nova, `article_filter_list`:

```python
# myproject/core/views.py
from dateutil.parser import parse
from datetime import timedelta
from django.shortcuts import render
from .models import Article
from .filters import ArticleFilter


...


def article_filter_list(request):
    template_name = 'core/article_filters_list.html'
    object_list = Article.objects.all()
    article_list = ArticleFilter(request.GET, queryset=object_list)

    context = {
        'object_list': object_list,
        'filter': article_list
    }
    return render(request, template_name, context)
```

O `ArticleFilter` recebe os dados do `request.GET` (o que foi digitado no formulário) e o queryset inicial. É ele que vai para o template com o nome `filter`.

Atenção ao nome do template: no vídeo a view foi escrita primeiro com `'core/article_filter_list.html'`, mas o arquivo criado se chama `article_filters_list.html`, e o resultado foi:

```
TemplateDoesNotExist at /articles/filter/
core/article_filter_list.html
```

O nome na view tem que ser exatamente o nome do arquivo.

## A rota e o menu

```python
# myproject/core/urls.py
from django.urls import path
from myproject.core import views as v


app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.person_list, name='person_list'),
    path('articles/', v.article_list, name='article_list'),
    path('articles/filter/', v.article_filter_list, name='article_filter_list'),
]
```

No `nav.html`, acrescente um item no menu, logo depois de "Artigos":

```html
<!-- myproject/core/templates/nav.html -->
            <li class="nav-item">
                <a class="nav-link" href="{% url 'core:article_list' %}">Artigos</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="{% url 'core:article_filter_list' %}">Artigos com filtros</a>
            </li>
```

## O template

Crie `article_filters_list.html` (no vídeo ele começou como uma cópia do `article_list.html`, e o formulário de datas foi removido):

```html
<!-- myproject/core/templates/core/article_filters_list.html -->
{% extends "base.html" %}

{% block content %}
  <div class="row">
    <div class="col-md-4">
      <h1>Lista de Artigos</h1>
    </div>
  </div>

  <div class="row">
    <div class="col-md-4">
      <form method="GET">
        {{ filter.form.as_p }}
        <input type="submit" />
      </form>
    </div>

    <div class="col-md-8">
      <table class="table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Sub-título</th>
            <th>Data de publicação</th>
          </tr>
        </thead>
        <tbody>
          {% for obj in filter.qs %}
            <tr>
              <td>{{ obj.title }}</td>
              <td>{{ obj.subtitle }}</td>
              <td>{{ obj.published_date }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
{% endblock content %}
```

Os dois pontos do django-filter no template:

* `{{ filter.form.as_p }}`: o `FilterSet` gera um formulário com um campo para cada filtro, cada um num parágrafo. O rótulo vem do `verbose_name` do modelo mais o lookup, e o HTML gerado fica assim:

```html
<p><label for="id_title">Título contains:</label> <input type="text" name="title" id="id_title"></p>
<p><label for="id_subtitle">Sub-título contains:</label> <input type="text" name="subtitle" id="id_subtitle"></p>
```

* `{% for obj in filter.qs %}`: o `.qs` é o queryset **já filtrado**. É preciso iterar sobre o `filter.qs`, e não sobre o `object_list`, que continua com todos os artigos.

O formulário usa `method="GET"`, então os filtros vão na URL, por exemplo `/articles/filter/?title=python&subtitle=2`.

## Testando

Rode o servidor e acesse "Artigos com filtros" no menu (`http://localhost:8000/articles/filter/`). O resultado, rodado com Django 2.2 e django-filter 2.3.0:

| Título contém | Sub-título contém | Resultado |
|---|---|---|
| (vazio) | (vazio) | os 6 artigos |
| `django` | (vazio) | Django Admin, Django Autoslug, Django Boilerplate, Django extensions |
| `python` | (vazio) | Dicas de Python, Dicas de Python 2 |
| `python` | `2` | Dicas de Python 2 |

Quando os dois campos são preenchidos, os filtros são combinados com "e": o título tem que conter `python` **e** o sub-título tem que conter `2`.

O formulário gerado não tem as classes do Bootstrap, então fica com uma aparência simples; o foco aqui é o funcionamento.

## Usando o filtro na view existente

Outra forma, que era a do texto original desta dica, é usar o `ArticleFilter` direto na view `article_list` e mandar o filtro para o template com os dois nomes:

```python
# myproject/core/views.py
from .filters import ArticleFilter


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()
    article_filter = ArticleFilter(request.GET, queryset=object_list)

    ...

    context = {
        'object_list': article_filter,
        'filter': article_filter
    }
    return render(request, template_name, context)
```

O template é o mesmo mostrado acima (`{{ filter.form.as_p }}` e `{% for obj in filter.qs %}`).
