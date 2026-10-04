# Dica 5 - Django Admin Date Range filter

**Versões usadas no vídeo:** Django 2.2.13, django-daterange-filter 1.3.0 e Python 3.8.2.
{: .versoes }

<a href="https://youtu.be/s5QzePekrvQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Repositório: [https://github.com/tzulberti/django-datefilterspec](https://github.com/tzulberti/django-datefilterspec)

O `list_filter` do admin do Django, quando aplicado a um campo de data, só oferece opções fixas: "Qualquer data", "Hoje", "Últimos 7 dias", "Este mês", "Este ano". Para filtrar por um **intervalo de datas qualquer** (de tal dia até tal dia), usamos a biblioteca **django-daterange-filter**, que acrescenta ao filtro dois campos de data com calendário.

Esta dica continua a [Dica 4](004-django-admin-personalizado.md): vamos acrescentar o filtro por data de publicação ao admin de artigos.

O repositório da biblioteca está marcado como **ABANDONED** (abandonado). O aviso aponta para um [pull request](https://github.com/tzulberti/django-datefilterspec/pull/17) com mais informações, e o projeto aceita contribuições de quem quiser mantê-lo. Mesmo assim, ele funcionou bem no vídeo, com o Django 2.2.

## Pré-requisitos

O projeto das dicas 3 e 4 (`myproject`, app `core`, models `Article` e `Category`, com os artigos já cadastrados) e o `admin.py` personalizado na Dica 4.

## Instalação

```bash
pip install django-daterange-filter
```

```
Installing collected packages: django-daterange-filter
    Running setup.py install for django-daterange-filter ... done
Successfully installed django-daterange-filter-1.3.0
```

Repare que o pacote se chama `django-daterange-filter`, mas o app é `daterange_filter`, com *underline*. Acrescente-o ao `INSTALLED_APPS` (ele traz um template próprio para o filtro, por isso precisa estar instalado como app):

```python
# settings.py
INSTALLED_APPS = (
    ...
    'daterange_filter'
)
```

No projeto do boilerplate fica assim:

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'daterange_filter',
    'myproject.core'
]
```

## Usando o DateRangeFilter no admin

Importe o `DateRangeFilter`:

```python
from daterange_filter.filter import DateRangeFilter
```

No `list_filter`, em vez de passar só o nome do campo, passe uma **tupla** com o nome do campo e a classe do filtro: `('published_date', DateRangeFilter)`. Os outros filtros continuam funcionando normalmente ao lado:

```python
# admin.py
from daterange_filter.filter import DateRangeFilter

...

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...
    list_filter = (
        ('published_date', DateRangeFilter),
        'category',
    )
```

Atenção às vírgulas: `list_filter` é uma tupla de filtros, e o primeiro item é ele mesmo uma tupla `(campo, filtro)`.

O `admin.py` completo, com o que já tínhamos da Dica 4:

```python
# myproject/core/admin.py
from django.conf import settings
from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from .models import Article, Category
# from .forms import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_published_date')
    search_fields = ('title',)
    list_filter = (
        ('published_date', DateRangeFilter),
        'category',
    )
    readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```

## Resultado

Suba o servidor e abra **Artigos** no admin:

```bash
python manage.py runserver
```

Na barra lateral **Filter** aparece, acima de "By categoria", o filtro "By criado em" (o admin do vídeo está em inglês; "criado em" é o `verbose_name` do campo `published_date`), com dois campos de data, cada um com o atalho "Today" e o ícone de calendário, e os botões **Search** e **Clear**.

No vídeo, todos os artigos foram criados em 14/06/2020:

* Com o intervalo de 2020-06-16 a 2020-06-25, nenhum artigo é listado.
* Com o intervalo de 2020-06-14 a 2020-06-25, os 4 artigos aparecem.

O filtro vai para a URL com o prefixo `drf__`, por exemplo:

```
/admin/core/article/?drf__published_date__gte=2020-06-14&drf__published_date__lte=2020-06-25
```

Ou seja, ele usa os lookups `__gte` (maior ou igual) e `__lte` (menor ou igual) no campo de data.

Observação: o django-daterange-filter 1.3.0 importa `django.contrib.admin.templatetags.admin_static`, que foi removido no Django 3.0, por isso ele só funciona até o Django 2.2. Em versões mais novas do Django, use uma alternativa mantida, como o `django-admin-rangefilter`.
