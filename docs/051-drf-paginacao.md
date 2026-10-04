# Dica 51 - DRF: paginação

**Versões usadas no vídeo:** Django 3.2.7, Django REST framework 3.12.4, django-seed 0.3.1 e Python 3.9.
{: .versoes }

<a href="https://youtu.be/UqES8tphzsQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/pagination](https://www.django-rest-framework.org/api-guide/pagination)

Continuando a série sobre Django REST framework, vamos ver como fazer **paginação** no DRF, de quatro maneiras diferentes:

1. `LimitOffsetPagination`;
2. `PageNumberPagination`;
3. paginação personalizada, global e só para uma view;
4. `CursorPagination`.

## Pré-requisitos

* O projeto `drf-example` das dicas anteriores, com a app `blog` (models `Author` e `Post`), criada com o dr-scaffold na [Dica 45](045-drf-scaffold.md). As rotas são `blog/authors/` e `blog/posts/`.

## Preparando o projeto

### django-seed

Para ter bastante dado para paginar, vamos precisar do [django-seed](041-django-seed.md):

```bash
source .venv/bin/activate
pip install django-seed
```

Editar `settings.py`

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
    'django_seed',
    # my apps
    ...
]
```

### Ajustando os models do blog

Aproveite e arrume os models do blog. Os campos passam a ser obrigatórios (sem `null=True, blank=True`), cada model ganha um `__str__`, o `Author` perde o campo de data, e o campo de data do `Post` passa a se chamar `created` (vamos precisar desse nome no fim, para o `CursorPagination`).

Editar `blog/models.py`

```python
# blog/models.py
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name


class Post(models.Model):
    body = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.body
```

Antes os models eram assim (como o dr-scaffold gerou):

```python
# blog/models.py (antes)
class Author(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    body = models.TextField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
```

Gere a migration:

```bash
python manage.py makemigrations
```

O Django pergunta se o `create_date` do `Post` foi renomeado para `created` (responda `y`) e, como `name` e `body` deixaram de aceitar nulo, pede um valor padrão para as linhas que já existem: escolha a opção `1` e informe `1`. A saída termina assim:

```
Migrations for 'blog':
  blog/migrations/0002_auto_20211022_0636.py
    - Rename field create_date on post to created
    - Remove field create_date from author
    - Alter field name on author
    - Alter field body on post
```

No vídeo, o `migrate` deu erro por causa dos dados antigos. A solução foi apagar o banco e começar de novo, criando também o superusuário:

```bash
rm -f db.sqlite3
python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

Agora gere 250 registros para cada model do blog:

```bash
python manage.py seed blog --number=250
```

Se o seed der erro pedindo o `psycopg2`, instale:

```bash
pip install psycopg2-binary
```

### Liberando as views e simplificando os serializers

Para ficar mais fácil testar no navegador, as views do blog ficam sem exigir autenticação (`AllowAny`):

Editar `blog/views.py`

```python
# blog/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from blog.models import Author, Post
from blog.serializers import AuthorSerializer, PostSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (AllowAny,)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
```

E os serializers trocam o `HyperlinkedModelSerializer` por `ModelSerializer`, assim aparece o `id` de cada item:

Editar `blog/serializers.py`

```python
# blog/serializers.py
from rest_framework import serializers

from blog.models import Author, Post


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
```

## LimitOffsetPagination

A paginação é configurada no `REST_FRAMEWORK`, com `DEFAULT_PAGINATION_CLASS` e `PAGE_SIZE`. Vamos deixar o `PAGE_SIZE` pequeno, só 5 itens, para ver a paginação funcionando.

Editar `settings.py`

```python
# backend/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5
}
```

Rode o servidor e abra [http://localhost:8000/blog/posts/](http://localhost:8000/blog/posts/):

```bash
python manage.py runserver
```

```json
{
    "count": 250,
    "next": "http://localhost:8000/blog/posts/?limit=5&offset=5",
    "previous": null,
    "results": [
        {
            "id": 1,
            "body": "Purpose community street life my simple. Interest similar special population ...",
            "created": "1981-11-10T10:48:38Z",
            "author": 127
        },
        ...
    ]
}
```

A resposta agora traz `count` (o total de itens), `next` e `previous` (os links da próxima página e da anterior) e `results` (os itens da página). O DRF também mostra os botões de paginação na página da API navegável.

Como funciona o limit/offset: o `limit` é a quantidade de itens por página (5) e o `offset` é a partir de qual item começar. A primeira página é `offset=0`, a segunda `offset=5`, a terceira `offset=10`, e assim por diante:

```
  limit=5      limit=5      limit=5
 [_______]    [_______]    [_______]
 offset=0     offset=5     offset=10
```

Se o limite fosse 3, os offsets seriam 0, 3, 6, 9...

O `PAGE_SIZE` é só o valor padrão: no `LimitOffsetPagination` o `limit` é variável, quem chama a API pode mudar. Por exemplo, `http://localhost:8000/blog/posts/?limit=3&offset=5` devolve só 3 itens.

## PageNumberPagination

A outra opção, mais comum (e a que o Regis mais gosta de usar), é a paginação por número de página: página 1, página 2, página 3...

Editar `settings.py`

```python
# backend/settings.py
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}
```

Rode o servidor de novo e abra `http://localhost:8000/blog/posts/`. O `next` agora é `http://localhost:8000/blog/posts/?page=2`, e você navega com `?page=3`, `?page=4`... Aqui o tamanho da página é fixo: quem chama a API não consegue mais mudar o `PAGE_SIZE`.

## Paginação personalizada global (Custom Pagination)

E se você quiser uma paginação personalizada, para o projeto inteiro? Basta criar uma classe que herda de uma das paginações do DRF e mudar os atributos.

Crie uma app `core` só para guardar essa classe, e apague o que não vai ser usado:

```bash
python manage.py startapp core
rm -f core/{admin,models,tests,views}.py
rm -rf core/migrations
touch core/pagination.py
```

Adicione a app em `INSTALLED_APPS`:

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    'django_seed',
    # my apps
    'core',
    'accounts',
    'blog',
    'product',
    'ecommerce',
]
```

Editar `core/pagination.py`

```python
# core/pagination.py
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

* `page_size`: 10 itens por página (vale mais que o `PAGE_SIZE` do settings).
* `page_size_query_param`: o nome do parâmetro com que quem chama a API pode mudar o tamanho da página, por exemplo `?page_size=20`.
* `max_page_size`: o máximo que pode ser pedido no `page_size`.

Editar `settings.py`

```python
# backend/settings.py
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 5
}
```

Rode o servidor de novo: em vez de 5, agora cada página tem 10 itens (veja pelo `id`, que vai de 1 até 10 na primeira página).

## Paginação personalizada para o blog

E se você quiser uma paginação diferente só para uma view? Por exemplo, só para os posts do blog. Crie um `pagination.py` dentro da app `blog`:

Editar `blog/pagination.py`

```python
# blog/pagination.py
from rest_framework.pagination import PageNumberPagination


class CustomBlogResultsSetPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 70
```

E use no `PostViewSet`, com o atributo `pagination_class`:

Editar `blog/views.py`

```python
# blog/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from blog.models import Author, Post
from blog.pagination import CustomBlogResultsSetPagination
from blog.serializers import AuthorSerializer, PostSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (AllowAny,)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomBlogResultsSetPagination
```

Rode o servidor de novo. Em `http://localhost:8000/blog/posts/` agora são 7 itens por página. Já em `http://localhost:8000/blog/authors/` continuam 10, porque os autores usam a paginação global, definida no settings.

No terminal do `runserver` aparece este aviso:

```
UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'blog.models.Post'> QuerySet.
```

Ele avisa que o queryset não tem ordenação; para paginar de forma consistente, o ideal é ordenar (com `ordering` no `Meta` do model ou `.order_by()` no queryset).

## Cursor Pagination

A última opção, também na documentação, é o `CursorPagination`. Comente a linha anterior e coloque esta:

Editar `settings.py`

```python
# backend/settings.py
REST_FRAMEWORK = {
    ...
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 5
}
```

Para testar nos posts, comente o `pagination_class` do `PostViewSet`, senão ele continua usando a paginação do blog (no vídeo, deixar os dois juntos deu erro):

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    # pagination_class = CustomBlogResultsSetPagination
```

O resultado:

```json
{
    "next": "http://localhost:8000/blog/posts/?cursor=cD0yMDIxLTA5LTE2...",
    "previous": null,
    "results": [
        {
            "id": 190,
            "body": "Buy season same artist election rest. Consumer movement glass doctor economic ...",
            "created": "2021-09-16T02:21:22Z",
            "author": 46
        },
        ...
    ]
}
```

A diferença: não tem `count`, e o link da página é um `cursor` codificado, então você não sabe a sequência das páginas; só existem **next** e **previous**. É interessante quando você não quer que alguém (um robô, por exemplo) fique navegando direto para uma página qualquer da sua aplicação.

> Requer um campo com o nome `created` no seu modelo.

Foi por isso que lá no começo trocamos `create_date` por `created` no `Post`. Por padrão o `CursorPagination` ordena por `-created` (do mais novo para o mais antigo); se o seu model não tiver esse campo, a aplicação dá erro. Dá para mudar o campo com o atributo `ordering` numa classe que herda de `CursorPagination`.

Essas são as quatro maneiras de paginar no DRF: `LimitOffsetPagination`, `PageNumberPagination`, uma classe personalizada (global ou por view) e `CursorPagination`.
