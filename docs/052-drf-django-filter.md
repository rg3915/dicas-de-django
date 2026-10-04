# Dica 52 - DRF: django-filter

**Versões usadas no vídeo:** Django 3.2.7, Django REST framework 3.12, django-filter 21.1 e Python 3.9.
{: .versoes }

<a href="https://youtu.be/J8mKLw_Txok">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend)

Doc: [https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf)

Continuando a série sobre Django REST framework, vamos ver várias formas de **filtrar** os dados de uma API:

1. filtrando a queryset fixa;
2. filtrando pelo usuário logado;
3. filtrando a partir de query parameters (`?username=regis`);
4. filtro genérico com o [django-filter](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf);
5. filtro específico com `filterset_class`;
6. campo de busca com `SearchFilter`.

Vamos mexer só na app `blog`.

## Pré-requisitos

* O projeto `drf-example` das dicas anteriores, com a app `blog` (models `Author` e `Post`) e o django-seed instalado ([Dica 51](051-drf-paginacao.md)).
* Pelo menos dois usuários: no vídeo, `admin` e `regis`.

## Filtrando a queryset

### Ajustando os models

Primeiro vamos arrumar os models do blog. O `Author` troca o `name` por `first_name` e `last_name` (com uma property `full_name`), e o `Post` ganha um `title` e um `created_by`, apontando para o `User` do Django, para sabermos quem criou o post.

Editar `blog/models.py`

```python
# blog/models.py
from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True)

    class Meta:
        verbose_name_plural = "Authors"

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


class Post(models.Model):
    title = models.CharField(max_length=30)
    body = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='criado por',
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title
```

O `full_name` junta o primeiro e o último nome; como `last_name` pode ser nulo, o `or ""` evita aparecer `None`, e o `.strip()` tira o espaço que sobraria no fim.

### Admin

Editar `blog/admin.py`

```python
# blog/admin.py
from django.contrib import admin

from blog.models import Author, Post


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_by')
```

Atenção à vírgula em `('__str__',)`. Sem ela, o Python entende uma string, e não uma tupla, e o Django reclama:

```
ERRORS:
<class 'blog.admin.AuthorAdmin'>: (admin.E107) The value of 'list_display' must be a list or tuple.
```

### Migrations e dados

```bash
python manage.py makemigrations
```

Como `first_name` e `title` são obrigatórios e já existem registros, o Django pede um valor padrão. Nos dois casos, escolha a opção `1` e informe `1`. Depois:

```bash
python manage.py migrate
python manage.py seed blog --number=120
```

### A queryset fixa

Agora a primeira forma de filtrar: direto no `queryset` da view. No `PostViewSet`, comente o `queryset` original e filtre pelos posts criados pelo usuário `regis`. Aproveite e volte a exigir autenticação, e comente a paginação personalizada do blog:

Editar `blog/views.py`

```python
# blog/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from blog.models import Author, Post
from blog.pagination import CustomBlogResultsSetPagination
from blog.serializers import AuthorSerializer, PostSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (AllowAny,)


class PostViewSet(viewsets.ModelViewSet):
    # queryset = Post.objects.all()
    queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination
```

O `created_by__username` atravessa a ForeignKey: filtra pelo campo `username` do `User` ligado em `created_by`.

Rode o servidor e, no Admin, defina o **Criado por** de alguns posts: no vídeo, um como `admin` e dois como `regis`.

```bash
python manage.py runserver
```

Em [http://localhost:8000/blog/posts/](http://localhost:8000/blog/posts/) aparecem só os dois posts criados pelo `regis`:

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 398,
            "title": "That office pressure current a",
            "body": "Road take case them. Day usually institution especially PM. ...",
            "created": "2020-09-14T06:20:20Z",
            "author": 622,
            "created_by": 24
        },
        {
            "id": 399,
            "title": "Special part piece tend.",
            "body": "Whole understand much onto mind unit. Worry good admit talk today rather. ...",
            "created": "2008-07-02T01:59:20Z",
            "author": 646,
            "created_by": 24
        }
    ]
}
```

## Filtrando pelo usuário logado

Em vez de fixar o `regis`, vamos mostrar só os posts do usuário que está logado. Para isso, comente o `queryset` e sobrescreva o método `get_queryset`, que tem acesso ao `self.request`:

Editar `blog/views.py`

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    # queryset = Post.objects.all()
    # queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(created_by=user)
```

Ao rodar o servidor, dá este erro:

```
AssertionError: `basename` argument not specified, and could not automatically determine the name from the viewset, as it does not have a `.queryset` attribute.
```

O router usa o `queryset` da view para descobrir o nome das rotas. Sem o atributo `queryset`, você tem que informar o `basename` (o nome do model) no `register`:

Editar `blog/urls.py`

```python
# blog/urls.py
from django.urls import include, path
from rest_framework import routers

from blog.views import AuthorViewSet, PostViewSet

router = routers.DefaultRouter()

router.register(r'authors', AuthorViewSet, basename='Author')
router.register(r'posts', PostViewSet, basename='Post')

urlpatterns = [
    path("", include(router.urls)),
]
```

Logado como `admin`, a lista mostra só os posts criados pelo `admin`. Se você mudar outro post para `admin` no Admin do Django, ele também passa a aparecer.

No vídeo, para que o navegador use o login da sessão (e não o JWT), foi comentada a autenticação JWT no settings:

Editar `settings.py`

```python
# backend/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    ...
}
```

## Filtrando a partir de query parameters

Agora vamos filtrar pelo que vier na URL, por exemplo `?username=regis`. Comente o `get_queryset` anterior e escreva outro, que lê o parâmetro em `self.request.query_params`:

Editar `blog/views.py`

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    # queryset = Post.objects.all()
    # queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination

    # def get_queryset(self):
    #     user = self.request.user
    #     return Post.objects.filter(created_by=user)

    def get_queryset(self):
        queryset = Post.objects.all()
        username = self.request.query_params.get('username')

        if username:
            queryset = queryset.filter(created_by__username=username)
        return queryset
```

Sem o parâmetro, a lista traz todos os posts. Com [http://localhost:8000/blog/posts/?username=regis](http://localhost:8000/blog/posts/?username=regis), só os posts criados pelo `regis`.

Dá para combinar vários parâmetros. Por exemplo, também filtrando por parte do título com `?title=`:

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Post.objects.all()
        username = self.request.query_params.get('username')

        if username is not None:
            queryset = queryset.filter(created_by__username=username)

        title = self.request.query_params.get('title')

        if title is not None:
            queryset = queryset.filter(title__icontains=title)

        return queryset
```

## Filtro Genérico django-filter

Escrever um `if` para cada parâmetro cansa. O [django-filter](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf) faz isso de forma genérica.

```bash
pip install django-filter

pip freeze | grep django-filter >> requirements.txt
```

No vídeo foi instalada a versão `django-filter==21.1`.

Editar `settings.py`

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    # 3rd apps
    'django_filters',
    'rest_framework',
    ...
]

REST_FRAMEWORK = {
    ...
    'PAGE_SIZE': 5,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
```

Na view, volte o `queryset = Post.objects.all()` (o `DjangoFilterBackend` filtra a partir dele), comente o `get_queryset` e diga em quais campos dá para filtrar com `filterset_fields`:

Editar `blog/views.py`

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    # queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination
    filterset_fields = ('title', 'body')

    # def get_queryset(self):
    #     ...
```

No vídeo, o primeiro teste deu erro justamente porque o `get_queryset` foi comentado, mas o `queryset` principal ainda não tinha sido descomentado.

Agora, na API navegável, aparece o botão **Filtros**, e você filtra pela URL, por exemplo:

```
http://localhost:8000/blog/posts/?title=Argue%20laugh%20others%20economic%20jo
```

Só que repare no problema: o `filterset_fields` compara o **texto completo** (`exact`). Você tem que escrever o título ou o corpo inteiro, exatamente igual; um pedaço da frase não retorna nada.

## Adicionando filtro específico com filterset_class

A solução é criar uma classe de filtro, dizendo como cada campo deve ser comparado. Crie o arquivo `blog/filters.py`:

```python
# blog/filters.py
from django_filters import rest_framework as filters

from blog.models import Post


class PostFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    body = filters.CharFilter(field_name='body', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ('title', 'body')
```

O `lookup_expr='icontains'` faz a busca por **parte do texto**, sem diferenciar maiúsculas e minúsculas (é o `title__icontains` do ORM).

E na view troque o `filterset_fields` por `filterset_class`:

Editar `blog/views.py`

```python
# blog/views.py
from blog.filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    # queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination
    # filterset_fields = ('title', 'body')
    filterset_class = PostFilter
```

Agora basta uma palavra: `http://localhost:8000/blog/posts/?body=some` ou `http://localhost:8000/blog/posts/?title=skin` retornam todos os posts que contêm o texto.

## Campo de busca

Por fim, um campo de busca, com o `SearchFilter` do próprio DRF. Vamos colocar no `AuthorViewSet`:

Editar `blog/views.py`

```python
# blog/views.py
from rest_framework.filters import SearchFilter


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name')
```

* `filter_backends`: aqui só o `SearchFilter`, para não poluir a página com os filtros do django-filter.
* `search_fields`: os campos em que a busca procura.

Rode o servidor e abra `http://localhost:8000/blog/authors/?search=michael`: aparecem os autores com "Michael" no nome. Com `?search=jones`, os que têm "Jones" no sobrenome:

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 650,
            "first_name": "Cynthia",
            "last_name": "Jones"
        },
        {
            "id": 651,
            "first_name": "Melanie",
            "last_name": "Jones"
        }
    ]
}
```

## views.py completo

Ao final, o `blog/views.py` fica assim (com as versões anteriores do `get_queryset` comentadas, para consulta):

```python
# blog/views.py
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from blog.filters import PostFilter
from blog.models import Author, Post
from blog.pagination import CustomBlogResultsSetPagination
from blog.serializers import AuthorSerializer, PostSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    # queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination
    # filterset_fields = ('title', 'body')
    filterset_class = PostFilter

    # def get_queryset(self):
    #     user = self.request.user
    #     return Post.objects.filter(created_by=user)

    # def get_queryset(self):
    #     queryset = Post.objects.all()
    #     username = self.request.query_params.get('username')

    #     if username:
    #         queryset = queryset.filter(created_by__username=username)
    #     return queryset
```

Com isso você tem desde o filtro mais simples, direto na queryset, até o filtro genérico do django-filter e a busca por texto do `SearchFilter`.
