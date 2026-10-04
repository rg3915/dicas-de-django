# Dica 39 - Django Admin: display decorator (Django 3.2+)

**Versões usadas no vídeo:** Django 3.2.5 e Python 3.9 (projeto criado com o django-boilerplate).
{: .versoes }

<a href="https://youtu.be/lKEPuwBjHss">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator)

O Django 3.2 trouxe uma novidade para o Admin: o decorator `@admin.display`. Ele serve para configurar os métodos que você coloca no `list_display` (ou no `readonly_fields`): o título da coluna, se o valor é um booleano (e deve aparecer com os ícones de "sim" e "não") e por qual campo a coluna é ordenada.

Antes dele, isso era feito com atributos pendurados na função (`short_description`, `boolean`, `admin_order_field`), como vimos na [Dica 28 - Admin: usando short description](028-admin-usando-short-description.md). Esse jeito antigo ainda funciona; o decorator só deixa tudo junto, em cima do método.

A assinatura, segundo a documentação, é:

```python
display(*, boolean=None, ordering=None, description=None, empty_value=None)
```

Neste tutorial vamos usar três desses parâmetros: `description`, `boolean` e `ordering`.

## Pré-requisitos

**IMPORTANTE:** para mostrar essa feature, o vídeo usou um projeto separado, criado com o [django-boilerplate](https://github.com/rg3915/django-boilerplate) (veja a [Dica 1.1 - Django boilerplate](001-django-boilerplate.md)), e não o projeto principal das dicas.

O projeto foi criado com o nome `backend`, escolhendo o Django 3.2 no menu do script:

```bash
git clone https://github.com/rg3915/django-boilerplate.git /tmp/django-boilerplate
cp /tmp/django-boilerplate/boilerplatesimple.sh .
source boilerplatesimple.sh backend
```

```
Select Django version:
2 - 2.2.*
3 - 3.2.*
Choose from 2, 3 [3]: 3
```

Confira a versão:

```bash
pip freeze | grep Django
# Django==3.2.5
```

O boilerplate cria a app `backend/crm`, com um modelo `Person` e o respectivo `PersonAdmin`.

## O modelo

Em `backend/crm/models.py`, acrescente o campo `published_date` (data de publicação) ao `Person`. É um `DateField` opcional:

```python
# backend/crm/models.py
from django.db import models
from django.urls import reverse_lazy

from backend.core.models import (
    Active,
    Address,
    Document,
    TimeStampedModel,
    UuidModel
)


class Person(UuidModel, TimeStampedModel, Address, Document, Active):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)
    published_date = models.DateField('data de publicação', null=True, blank=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse_lazy('crm:person_detail', kwargs={'pk': self.pk})
```

Os modelos abstratos `UuidModel`, `TimeStampedModel`, `Address`, `Document` e `Active` vêm do `backend/core/models.py` do boilerplate (o `Active` é o que fornece o campo booleano `active`).

A app `crm` do boilerplate vem sem migrações, então crie e aplique:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Migrations for 'crm':
  backend/crm/migrations/0001_initial.py
    - Create model Person
...
  Applying crm.0001_initial... OK
```

## O jeito antigo: short_description

Em `backend/crm/admin.py`, vamos mostrar a data de publicação formatada como `dd/mm/aaaa` numa coluna da listagem. Para isso criamos o método `get_published_date` e colocamos o nome dele no `list_display`. Antes do Django 3.2, o título da coluna era definido assim:

```python
# backend/crm/admin.py
from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'get_published_date', 'active')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('active',)

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

O método recebe o objeto da linha (`obj`) e devolve o que vai aparecer na célula. Sem o `short_description`, o título da coluna seria o nome do método ("Get published date").

Suba o servidor, entre no Admin e cadastre uma pessoa com a data de publicação preenchida:

```bash
python manage.py runserver
```

A listagem mostra a coluna **Data de publicação** com a data no formato `15/07/2021`.

## O jeito novo: @admin.display(description=...)

A partir do Django 3.2, troque o atributo pelo decorator:

```python
    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')
```

O resultado é o mesmo, mas a configuração fica junto da definição do método. Atenção à grafia: é `description`. No vídeo, um erro de digitação no nome do parâmetro derrubou o servidor, porque o `display` só aceita argumentos nomeados (`boolean`, `ordering`, `description` e `empty_value`).

## Colunas booleanas: boolean=True

Agora vamos criar uma coluna que diz se a pessoa já foi publicada, ou seja, se `published_date` está preenchido:

```python
    @admin.display(description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```

E acrescente `'is_published'` no `list_display`. Repare que a coluna mostra o texto `True` ou `False`. Para mostrar os ícones verde e vermelho que o Admin usa nos campos booleanos, passe `boolean=True`:

```python
    @admin.display(boolean=True, description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```

Para testar, cadastre outra pessoa (no vídeo, "Zezinho") primeiro **sem** data de publicação: a coluna "Publicado" mostra o ícone vermelho e a "Data de publicação" mostra `-`. Edite e preencha a data: o ícone fica verde.

## Ordenando a coluna: ordering

Uma coluna calculada por um método não pode ser ordenada, porque o Admin não sabe qual campo do banco usar no `ORDER BY`. O parâmetro `ordering` diz isso a ele. Com `'-published_date'`, clicar no título "Publicado" ordena pela data de publicação, da mais recente para a mais antiga:

```python
    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```

No vídeo a ordem não mudou de primeira, por causa do `ordering = ('first_name',)` do `Meta` do modelo. Depois de comentar essa linha no `models.py`, a pessoa com data 16/07/2021 passou a aparecer antes da de 15/07/2021:

```python
    class Meta:
        # ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'
```

## O admin.py completo

```python
# backend/crm/admin.py
from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'get_published_date', 'is_published', 'active')  # noqa E501
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('active',)

    # def get_published_date(self, obj):
    #     if obj.published_date:
    #         return obj.published_date.strftime('%d/%m/%Y')

    # get_published_date.short_description = 'Data de Publicação'

    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```

## O mesmo exemplo com o modelo Article

No README do projeto das dicas, o mesmo recurso foi mostrado com o modelo `Article` (que tem um campo `published_date`). Antigamente:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date')

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

... e ainda funciona. A partir do Django 3.2:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date', 'is_published')

    # Django 3.2+
    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```

## Conclusão

O `@admin.display` não muda o que o Admin consegue fazer; ele junta numa linha, em cima do método, o que antes ficava espalhado em atributos (`short_description`, `boolean`, `admin_order_field`). Há ainda o parâmetro `empty_value`, que define o que aparece quando o método devolve um valor vazio (o padrão é `-`). Os detalhes estão na [documentação](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator).
