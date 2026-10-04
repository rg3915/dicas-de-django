# Dica 28 - Admin: Usando short description

**Versões usadas no vídeo:** Django 2.2.15 e Python 3.8.
{: .versoes }

<a href="https://youtu.be/Uwwr77SR8EE">
    <img src="../.gitbook/assets/youtube.png">
</a>


Quando não conseguimos usar o `dunder` no `list_display` do admin, então usamos o `short_description`.

Neste tutorial vamos ver o erro que aparece quando tentamos mostrar o campo de um model relacionado no `list_display` usando `__` (o *dunder*, *double underscore*), como resolvê-lo com um método no `ModelAdmin` e como dar um título bonito à coluna com o `short_description`. O mesmo recurso também serve para formatar um valor, como uma data no formato dia/mês/ano. Isso já tinha aparecido na [dica 4 - Django Admin personalizado](004-django-admin-personalizado.md); aqui vemos o problema e a solução em detalhe.

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django), com os models `Article` e `Category`. O que importa aqui é que `Article` tem uma `ForeignKey` para `Category`, e `Category` tem o campo `title`:

```python
# myproject/core/models.py
import uuid
from django.db import models
from autoslug import AutoSlugField
from hashid_field import HashidAutoField


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


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


class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

## O problema: dunder no list_display

Queremos mostrar o título da categoria na lista de artigos do Admin. Como no ORM escrevemos `category__title` para chegar ao título da categoria (por exemplo, em `Article.objects.filter(category__title='Python')`), a primeira tentativa é colocar isso no `list_display`:

```python
# myproject/core/admin.py
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'get_published_date', 'category__title')
    ...
```

Ao rodar o servidor, o Django nem sobe:

```
$ python manage.py runserver
...
django.core.management.base.SystemCheckError: SystemCheckError: System check identified some issues:

ERRORS:
<class 'myproject.core.admin.ArticleAdmin'>: (admin.E108) The value of 'list_display[4]' refers to 'category__title', which is not a callable, an attribute of 'ArticleAdmin', or an attribute or method on 'core.Article'.
```

O erro diz tudo: cada item do `list_display` precisa ser um campo, um atributo ou um método do model, ou um método (*callable*) do `ModelAdmin`. O `__` funciona em `search_fields`, `list_filter` e `ordering`, mas **não** funciona no `list_display` do Django 2.2 usado no vídeo.

No vídeo aparece também um aviso (`HashidField.W001 'salt' is not set`), que vem do django-hashid-field e não tem relação com este erro.

## A solução: um método no ModelAdmin com short_description

Criamos um método no `ArticleAdmin` que recebe o objeto da linha (`obj`) e devolve o que queremos mostrar. Depois colocamos o **nome do método** no `list_display`:

```python
# myproject/core/admin.py
from django.conf import settings
from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from .models import Article, Category
# from .forms import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'get_published_date', 'get_category')
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

    def get_category(self, obj):
        if obj.category:
            return obj.category.title

    get_category.short_description = 'Categoria'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```

O que mudou foi o método `get_category`:

```python
    def get_category(self, obj):
        if obj.category:
            return obj.category.title

    get_category.short_description = 'Categoria'
```

* `obj` é o artigo da linha que está sendo desenhada.
* O `if obj.category` é necessário porque a categoria é opcional (`null=True`): sem ele, um artigo sem categoria daria `AttributeError: 'NoneType' object has no attribute 'title'`. Quando o método devolve `None`, o Admin mostra um traço (`-`).
* `short_description` é o título da coluna. Sem ele, o Admin usaria o nome do método, e a coluna se chamaria "Get category".

Agora o `runserver` sobe normalmente e a lista de artigos ganha a coluna **Categoria** com o título da categoria de cada artigo.

## Outro uso: formatar um valor

O mesmo truque serve quando o campo existe, mas você quer mostrá-lo de outro jeito. É o caso do `get_published_date`, que já estava no projeto:

```python
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

Se colocássemos `'published_date'` direto no `list_display` (ou devolvêssemos `obj.published_date` sem o `strftime`), o Admin mostraria a data e a hora no formato padrão do idioma do projeto (com `LANGUAGE_CODE = 'en-us'`, algo como `Feb. 20, 2021, 6:20 p.m.`). Com `strftime('%d/%m/%Y')` a coluna mostra só dia, mês e ano, por exemplo `20/02/2021`, e o `short_description` dá o título "Data de Publicação".

## Resumo

* No Django 2.2, o `list_display` não aceita `campo__outro_campo`.
* Crie um método no `ModelAdmin` que recebe `obj` e devolve o valor; coloque o nome do método no `list_display`.
* Use `metodo.short_description = 'Título'` para dar nome à coluna.

Observação: em versões mais novas do Django, o jeito recomendado de definir o título é o decorador `@admin.display(description='Categoria')` em cima do método (Django 3.2+), e a partir do Django 5.1 o `list_display` passou a aceitar `category__title`.
