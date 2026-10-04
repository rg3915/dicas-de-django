# Dica 18 - bulk_create e bulk_update

**Versões usadas no vídeo:** Django 2.2, Python 3.8, IPython 7.15 e django-extensions 2.2.
{: .versoes }

<a href="https://youtu.be/U99VT4UwJ5k">
    <img src="../.gitbook/assets/youtube.png">
</a>

Quando precisamos gravar ou alterar muitos registros de uma vez, o caminho óbvio é um `for` chamando `save()` em cada objeto. Funciona, mas cada `save()` é uma consulta separada ao banco: 100 objetos são 100 `INSERT` (ou 100 `UPDATE`). O Django tem dois métodos para fazer isso em lote, com uma única consulta (ou poucas):

* [bulk_create](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create): insere uma grande quantidade de dados no banco de forma super rápida.
* [bulk_update](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-update): como o nome já diz, atualiza os dados em lote (disponível a partir do Django 2.2).

Neste tutorial vamos gerar 100 títulos aleatórios, inserir 100 artigos com `bulk_create` e depois colocar todos eles numa categoria com `bulk_update`, tudo pelo `shell_plus`.

## Pré-requisitos

O vídeo usa o projeto do repositório [rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django), com o app `core` dentro de `myproject`. Para reproduzir você precisa de:

* Python 3.8 e Django 2.2.
* [django-extensions](https://django-extensions.readthedocs.io/en/latest/), para ter o `shell_plus` (veja a [Dica 2 - Django extensions](002-django-extensions.md)).
* IPython, opcional, para ter o shell colorido do vídeo.
* `django-autoslug` e `django-hashid-field`, que o modelo `Article` do projeto usa (o `slug` e o `id` com hash).

```bash
pip install Django==2.2.13 django-extensions==2.2.9 django-autoslug==1.9.7 django-hashid-field==3.1.3 ipython
```

No `settings.py`, o `django_extensions` e o app `core` precisam estar no `INSTALLED_APPS`:

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
    'myproject.core',
]
```

## Os modelos

Estes são os modelos do projeto na época do vídeo. Um `Article` tem título, subtítulo, slug gerado a partir do título e uma categoria opcional (`null=True, blank=True`), que é o campo que vamos preencher com o `bulk_update`.

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

```bash
python manage.py makemigrations
python manage.py migrate
```

No vídeo o banco já tinha 6 artigos e uma categoria chamada `dicas`, cadastrados antes pelo Admin. Se o seu banco estiver vazio, crie a categoria (no Admin ou no shell com `Category.objects.create(title='dicas')`).

## Abrindo o shell_plus

Vamos usar o

```bash
python manage.py shell_plus
```

A vantagem do `shell_plus` é que ele já importa todos os modelos do projeto. Na abertura ele mostra o que importou:

```
# Shell Plus Model Imports
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from myproject.core.models import Article, Category
# Shell Plus Django Imports
...
Python 3.8.2 (default, Apr 29 2020, 23:19:54)
IPython 7.15.0 -- An enhanced Interactive Python. Type '?' for help.
```

Ou seja, `Article` e `Category` já estão disponíveis, sem precisar de `from myproject.core.models import ...`.

## Gerando dados aleatórios

Primeiro vamos criar uns dados aleatórios: uma lista com 100 palavras de 12 letras minúsculas. Para isso usamos o módulo `secrets` (que existe desde o Python 3.6) e o `string`:

```python
import secrets
import string

N = 12
list_items = []

for i in range(100):
    res = ''.join(secrets.choice(string.ascii_lowercase) for i in range(N))
    list_items.append(res)
```

* `string.ascii_lowercase` é a string `'abcdefghijklmnopqrstuvwxyz'`.
* `secrets.choice(...)` sorteia uma letra; repetimos isso `N` vezes e juntamos tudo com `''.join(...)`.
* Cada palavra sorteada vai para `list_items`.

Conferindo:

```python
In [7]: len(list_items)
Out[7]: 100
```

## bulk_create

Agora vamos inserir os dados com `bulk_create`. A ideia é montar os objetos **na memória**, sem salvar, guardar todos numa lista auxiliar e mandar a lista inteira de uma vez para o banco:

```python
aux = []
for item in list_items:
    obj = Article(title=item, subtitle=item)
    aux.append(obj)

Article.objects.bulk_create(aux)
```

Repare que `Article(title=item, subtitle=item)` só cria a instância em Python; nada foi gravado ainda. Quem grava é o `bulk_create(aux)`, que faz o `INSERT` de todos os objetos numa única consulta e devolve a lista dos objetos criados:

```
[<Article: sleydxdiszjp>,
 <Article: zgghrwlceisc>,
 <Article: ytbytgcowagn>,
 ...
 <Article: sdbfkijdqenr>,
 <Article: owrapqjitbxq>]
```

Contando os artigos:

```python
In [11]: Article.objects.all().count()
Out[11]: 106
```

Eram 6 e entraram mais 100. No Admin (`http://localhost:8000/admin/core/article/`) eles aparecem com título e sub-título iguais e o slug preenchido.

## bulk_update

Se você abrir qualquer um desses artigos novos no Admin, vai ver que o campo **Categoria** está vazio, porque não definimos categoria no `bulk_create`. Vamos colocar todos na primeira categoria do banco.

```python
articles = Article.objects.all()
category = Category.objects.first()
```

```python
In [14]: category
Out[14]: <Category: dicas>
```

Agora alteramos o atributo `category` de cada artigo, **ainda só na memória**:

```python
for article in articles:
    article.category = category
```

"Cadê o `article.save()`?" Se colocarmos `article.save()` dentro do `for`, o Django vai fazer um `UPDATE` por artigo, um por um, e é aí que o processo demora. Em vez disso, mandamos tudo de uma vez:

```python
Article.objects.bulk_update(articles, ['category'])
```

O primeiro argumento é a lista (ou queryset) de objetos já alterados; o segundo é a lista dos campos que devem ser atualizados, aqui só `category`. Atualizando a página do Admin, os artigos aparecem com a categoria **dicas**, e todos ficaram com o mesmo valor, porque atribuímos a mesma categoria para todos.

O código completo, de forma resumida:

```python
articles = Article.objects.all()
category = Category.objects.first()
for article in articles:
    article.category = category

Article.objects.bulk_update(articles, ['category'])
```

## Cuidados

* O `bulk_create` e o `bulk_update` não chamam o método `save()` do modelo e não disparam os sinais `pre_save` e `post_save`. Se o seu modelo tem lógica no `save()`, ela não roda.
* Os dois aceitam o argumento `batch_size`, para dividir listas muito grandes em vários lotes (por exemplo `Article.objects.bulk_create(aux, batch_size=1000)`).
* O `bulk_update` só atualiza os campos que você passar na lista.

## Conclusão

Com `bulk_create` inserimos 100 artigos e com `bulk_update` atualizamos a categoria de todos, sem fazer uma consulta por objeto. Use bastante essas duas ferramentas sempre que precisar inserir ou atualizar muitos registros: elas são muito rápidas e eficientes.
