# 52 - DRF: django-filter

<a href="">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend)

Doc: [https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf)

## Filtrando a queryset

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

Editar `blog/views.py`

```python
# blog/views.py
from rest_framework.permissions import AllowAny, IsAuthenticated

class PostViewSet(viewsets.ModelViewSet):
    # queryset = Post.objects.all()
    queryset = Post.objects.filter(created_by__username='regis')
    serializer_class = PostSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsAuthenticated,)
    # pagination_class = CustomBlogResultsSetPagination
```



## Filtrando pelo usuário logado

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



Erro:

```
AssertionError: `basename` argument not specified, and could not automatically determine the name from the viewset, as it does not have a `.queryset` attribute.
```

Editar `blog/urls.py`

```python
# blog/urls.py
...
router.register(r'authors', AuthorViewSet, basename='Author')
router.register(r'posts', PostViewSet, basename='Post')
```



## Filtrando a partir de query parameters

Editar `settings.py`

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
```

Editar `blog/views.py`

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

https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html#integration-with-drf

```
pip install django-filter

pip freeze | grep django-filter >> requirements.txt
```

Editar `settings.py`

```python
# settings.py
INSTALLED_APPS = [
    ...
    # 3rd apps
    'django_filters',
    ...
]

REST_FRAMEWORK = {
    ...
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
```

Editar `blog/views.py`


```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('title', 'body')

# comentar def get_queryset(self)
```

Filtra pelo texto completo.


## Adicionando filtro específico com filterset_class

Editar `blog/filters.py`

```python
# blog/filters.py
from django_filters import rest_framework as filters

from blog.models import Post


class PostFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr='icontains')
    body = filters.CharFilter(field_name="body", lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ('title', 'body')
```

Editar `blog/views.py`


```python
# blog/views.py
from blog.filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    # filterset_fields = ('title', 'body')
    filterset_class = PostFilter
```


## Campo de busca

Editar `blog/views.py`


```python
# blog/views.py
from rest_framework.filters import SearchFilter

class AuthorViewSet(viewsets.ModelViewSet):
    ...
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name')
```


