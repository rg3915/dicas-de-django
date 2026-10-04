# Dica 27 - Retornando os nomes dos campos do model

**Versões usadas no vídeo:** Django 2.2.15, Python 3.8, django-extensions 2.2.9 e IPython 7.15.
{: .versoes }

<a href="https://youtu.be/lU2J5ZCJiyE">
    <img src="../.gitbook/assets/youtube.png">
</a>


Às vezes você precisa dos nomes dos campos de um model: para montar o cabeçalho de uma exportação em CSV, para gerar um formulário ou uma tabela dinâmica, para comparar dois registros campo a campo. Em vez de digitar a lista na mão (e esquecer de atualizá-la quando o model mudar), dá para pedir ao próprio Django, com a API `_meta` do model.

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django), com o [django-extensions](002-django-extensions.md) instalado (para ter o `shell_plus`) e o model `Article`, criado nas dicas anteriores ([dica 3](003-django-bulk_create-e-django-autoslug.md) e [dica 6](006-geradores-de-senhas-randomicas-uuid-hashids-secrets.md)):

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

Qualquer model serve; a técnica é a mesma para o seu projeto.

## Abrindo o shell_plus

```bash
$ python manage.py shell_plus
```

O `shell_plus` já importa todos os models do projeto (inclusive o `User` do Django e o nosso `Article`), então não precisamos de nenhum `import`. No vídeo, ele abre com o IPython e mostra os imports automáticos:

```
# Shell Plus Model Imports
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from myproject.core.models import Article, Category
...
Python 3.8.2 (default, Oct 13 2020, 10:39:13)
IPython 7.15.0 -- An enhanced Interactive Python. Type '?' for help.
```

Se você não usa o django-extensions, abra o `python manage.py shell` e importe os models: `from django.contrib.auth.models import User` e `from myproject.core.models import Article`.

## get_fields(): os campos do model

Todo model tem o atributo `_meta`, com as informações do model (nome da tabela, `verbose_name`, ordenação, campos etc.). O método `_meta.get_fields()` devolve uma tupla com **objetos** de campo:

```python
In [1]: User._meta.get_fields()
Out[1]:
(<ManyToOneRel: admin.logentry>,
 <django.db.models.fields.AutoField: id>,
 <django.db.models.fields.CharField: password>,
 <django.db.models.fields.DateTimeField: last_login>,
 <django.db.models.fields.BooleanField: is_superuser>,
 <django.db.models.fields.CharField: username>,
 <django.db.models.fields.CharField: first_name>,
 <django.db.models.fields.CharField: last_name>,
 <django.db.models.fields.EmailField: email>,
 <django.db.models.fields.BooleanField: is_staff>,
 <django.db.models.fields.BooleanField: is_active>,
 <django.db.models.fields.DateTimeField: date_joined>,
 <django.db.models.fields.related.ManyToManyField: groups>,
 <django.db.models.fields.related.ManyToManyField: user_permissions>)
```

## Só os nomes, com list comprehension

Cada objeto de campo tem o atributo `name`. Com uma *list comprehension*, ficamos só com os nomes:

```python
$ python manage.py shell_plus

>>> [field.name for field in User._meta.get_fields()]
['logentry',
 'id',
 'password',
 'last_login',
 'is_superuser',
 'username',
 'first_name',
 'last_name',
 'email',
 'is_staff',
 'is_active',
 'date_joined',
 'groups',
 'user_permissions']
```

E para o nosso model `Article`:

```python
>>> [field.name for field in Article._meta.get_fields()]
['id', 'title', 'subtitle', 'slug', 'category', 'published_date']
```

Repare no primeiro item da lista do `User`: `logentry` não é uma coluna da tabela de usuários. É a relação reversa criada pelo `LogEntry` do Admin (que tem uma `ForeignKey` para `User`). O `get_fields()` devolve também essas relações reversas e os campos `ManyToManyField` (`groups`, `user_permissions`).

## Variações úteis

Se você quer só os campos que viram colunas na tabela, sem relações reversas e sem many-to-many, use `_meta.fields` (ou `_meta.concrete_fields`):

```python
>>> [field.name for field in User._meta.fields]
['id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']
```

E, com o objeto de campo em mãos, dá para pegar outras informações, como o `verbose_name` (o rótulo do campo):

```python
>>> [field.verbose_name for field in Article._meta.fields]
['id', 'título', 'sub-título', 'slug', 'categoria', 'criado em']

>>> User._meta.get_field('email').verbose_name
'email address'
```

## Conclusão

`Model._meta.get_fields()` devolve todos os campos do model (inclusive relações reversas), e `[field.name for field in Model._meta.get_fields()]` transforma isso numa lista de nomes, sempre atualizada com o model.
