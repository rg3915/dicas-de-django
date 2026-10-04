# Dica 3 - Django bulk_create e django-autoslug

**Versões usadas no vídeo:** Django 2.2.13, django-autoslug 1.9.7, python-slugify 4.0.0 e Python 3.8.2.
{: .versoes }

<a href="https://youtu.be/Py-AG6S_vJI">
    <img src="../.gitbook/assets/youtube.png">
</a>

Nesta dica vamos ver dois assuntos juntos:

* **slug** e o **django-autoslug**: um campo que gera o slug automaticamente a partir de outro campo do model.
* **bulk_create**: inserir vários registros no banco de uma vez só, com uma única consulta, em vez de chamar `save()` (ou `create()`) um por um.

## Pré-requisitos

Um projeto Django com um app `core`. No vídeo foi usado o projeto criado com o `boilerplatesimple.sh` da [Dica 1](000-django-boilerplate-e-cookiecutter-django.md) (projeto `myproject`, app em `myproject/core`), que já traz o `django-extensions` e o `shell_plus` da [Dica 2](002-django-extensions.md).

## O que é um slug: python-slugify

Um **slug** é um texto transformado para poder ser usado numa URL: tudo em minúsculas, sem acentos, com os espaços trocados por hífen. Para ver isso na prática, use a biblioteca [python-slugify](https://pypi.org/project/python-slugify/):

```bash
pip install python-slugify
```

E no `python`:

```python
>>> from slugify import slugify
>>> text = 'Dicas de Django'
>>> slugify(text)
'dicas-de-django'
>>> url = f'example.com/{slugify(text)}'
>>> url
'example.com/dicas-de-django'
```

O mesmo código, como script:

```python
from slugify import slugify

text = 'Dicas de Django'
print(slugify(text))
url = f'example.com/{slugify(text)}'
```

É assim que blogs e lojas montam URLs legíveis, como `example.com/dicas-de-django`, em vez de `example.com/artigo/42`.

## django-autoslug

No Django, em vez de gerar o slug na mão, usamos o [django-autoslug](https://pypi.org/project/django-autoslug/). Ele fornece o `AutoSlugField`, que preenche o slug sozinho, a partir de outro campo, na hora de salvar.

```bash
pip install django-autoslug
```

Se você escrever o model antes de instalar, o `manage.py` reclama assim que é executado:

```
ModuleNotFoundError: No module named 'autoslug'
```

O pacote se chama `django-autoslug`, mas o módulo que importamos é `autoslug`. Ele não precisa entrar no `INSTALLED_APPS`.

## Os models

Vamos criar dois models no app `core`: `Article` (artigo) e `Category` (categoria).

```python
# myproject/core/models.py
from django.db import models
from autoslug import AutoSlugField


class Article(models.Model):
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


class Category(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

O que cada parte faz:

* `slug = AutoSlugField(populate_from='title')`: o slug é gerado a partir do `title`. "Django Boilerplate" vira `django-boilerplate`.
* `category`: uma `ForeignKey` para `Category`. Como `Category` está definida **depois** de `Article` no arquivo, passamos o nome do model como texto (`'Category'`). Com `on_delete=models.SET_NULL`, se a categoria for apagada, o artigo fica sem categoria em vez de ser apagado junto; por isso o campo precisa de `null=True` (e `blank=True` para ser opcional nos formulários).
* `published_date`: com `auto_now_add=True`, a data é gravada só na criação do registro; com `auto_now=False`, ela não muda quando o registro é editado.
* `ordering = ('title',)`: ordena por título. Repare na **vírgula**: `('title',)` é uma tupla; sem a vírgula, `('title')` seria só uma string.
* `Category.title` tem `unique=True`: não pode haver duas categorias com o mesmo nome.

Crie as tabelas:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Migrations for 'core':
  myproject/core/migrations/0001_initial.py
    - Create model Category
    - Create model Article
Running migrations:
  Applying core.0001_initial... OK
```

No vídeo, o `migrate` foi esquecido no começo, e o primeiro `bulk_create` deu erro porque a tabela ainda não existia. Se acontecer com você, saia do shell, rode os dois comandos acima e volte.

## bulk_create

O [bulk_create](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create) recebe uma lista de objetos (ainda não salvos) e insere todos no banco de uma vez, com um único `INSERT`. Para muitos registros, é muito mais rápido do que um `save()` por objeto.

Abra o `shell_plus` (ele já importa os models `Article` e `Category`):

```bash
python manage.py shell_plus
```

### Inserindo as categorias

A ideia é sempre a mesma: montar uma lista auxiliar com os objetos e passar a lista para o `bulk_create`:

```python
categories = [
    'dicas',
    'django',
    'python',
]

aux = []

for category in categories:
    obj = Category(title=category)
    aux.append(obj)

Category.objects.bulk_create(aux)
```

```
[<Category: dicas>, <Category: django>, <Category: python>]
```

Repare que `Category(title=category)` só cria o objeto na memória; nada vai para o banco até o `bulk_create`.

### Inserindo os artigos com a categoria

Agora considere uma lista de dicionários, cada um com título, subtítulo e o **nome** da categoria. Para gravar o artigo, precisamos do **objeto** `Category`, então buscamos a categoria pelo título. A categoria `'admin'` não existe, de propósito, para tratarmos esse caso:

```python
titles = [
    {
        'title': 'Django Boilerplate',
        'subtitle': 'Django Boilerplate',
        'category': 'dicas'
    },
    {
        'title': 'Django extensions',
        'subtitle': 'Django extensions',
        'category': 'dicas'
    },
    {
        'title': 'Django Admin',
        'subtitle': 'Django Admin',
        'category': 'admin'
    },
    {
        'title': 'Django Autoslug',
        'subtitle': 'Django Autoslug',
        'category': 'dicas'
    },
]

aux = []

for title in titles:
    category = Category.objects.filter(title=title['category']).first()
    article = dict(
        title=title['title'],
        subtitle=title['subtitle']
    )
    if category:
        obj = Article(category=category, **article)
    else:
        obj = Article(**article)
    aux.append(obj)

Article.objects.bulk_create(aux)
```

```
[<Article: Django Boilerplate>, <Article: Django extensions>, <Article: Django Admin>, <Article: Django Autoslug>]
```

Passo a passo:

* `Category.objects.filter(title=...).first()` devolve a categoria ou `None` se ela não existir. Com `.get()` daria uma exceção `DoesNotExist` para a categoria `'admin'`; o `.first()` evita isso.
* `article` é um dicionário com os campos do artigo, e `**article` desempacota esse dicionário como argumentos nomeados: `Article(**article)` é o mesmo que `Article(title='...', subtitle='...')`.
* Se a categoria existe, criamos o artigo com ela; senão, sem categoria (o campo aceita `null`).

E o slug? Não passamos nenhum, mas o `AutoSlugField` preencheu cada um a partir do título, mesmo usando `bulk_create`:

```python
>>> Article.objects.values_list('title', 'slug', 'category__title')
<QuerySet [('Django Admin', 'django-admin', None), ('Django Autoslug', 'django-autoslug', 'dicas'), ('Django Boilerplate', 'django-boilerplate', 'dicas'), ('Django extensions', 'django-extensions', 'dicas')]>
```

(A lista vem ordenada por título, por causa do `ordering` do model.)

## Cuidados com o bulk_create

* O `bulk_create` **não chama o método `save()`** do model nem dispara os sinais `pre_save` e `post_save`. Se o seu model faz algo importante no `save()`, isso não vai acontecer.
* O `AutoSlugField` funciona porque o slug é gerado no `pre_save` do próprio campo, que o Django chama também no `bulk_create`. Mas, como os objetos são inseridos juntos, o `AutoSlugField(unique=True)` não consegue garantir slugs únicos entre os objetos do mesmo lote.
* No SQLite (e em outros bancos, exceto PostgreSQL), os objetos devolvidos pelo `bulk_create` ficam sem o `pk` preenchido.

## Conclusão

Com o `AutoSlugField` o slug se resolve sozinho, e com o `bulk_create` você insere dezenas ou milhares de registros com uma consulta só, montando primeiro a lista de objetos e depois mandando tudo de uma vez.

Links:

* [python-slugify](https://pypi.org/project/python-slugify/)
* [bulk_create](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create)
* [django-autoslug](https://pypi.org/project/django-autoslug/)
