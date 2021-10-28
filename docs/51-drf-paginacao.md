# 51 - DRF: paginação

<a href="https://youtu.be/UqES8tphzsQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/pagination](https://www.django-rest-framework.org/api-guide/pagination)

Vamos precisar do [django-seed](https://www.dicas-de-django.com.br/41-django-seed)

```
pip install django-seed
```

Editar `settings.py`

```python
INSTALLED_APPS = [
    ...
    'django_seed',
```

Rodar o comando

```
python manage.py seed blog --number=250
```

Editar `blog/models.py`

```python
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

Editar `blog/views.py`

```python
from rest_framework.permissions import AllowAny

class AuthorViewSet(viewsets.ModelViewSet):
    ...
    permission_classes = (AllowAny,)

class PostViewSet(viewsets.ModelViewSet):
    ...
    permission_classes = (AllowAny,)
```

Editar `blog/serializers.py`

```python
class AuthorSerializer(serializers.ModelSerializer):
    ...

class PostSerializer(serializers.ModelSerializer):
    ...
```


## LimitOffsetPagination

Editar `settings.py`

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5
}
```

## PageNumberPagination

Editar `settings.py`

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}
```


## Paginação personalizada global (Custom Pagination)

> Criar app core

```
rm -f core/{admin,models,tests,views}.py
rm -rf core/migrations
touch core/pagination.py
```

Editar `core/pagination.py`

```python
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

Editar `settings.py`

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 5
}
```

## Paginação personalizada para o blog

Editar `blog/pagination.py`

```python
from rest_framework.pagination import PageNumberPagination


class CustomBlogResultsSetPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 70
```


Editar `blog/views.py`

```python
from blog.pagination import CustomBlogResultsSetPagination

class PostViewSet(viewsets.ModelViewSet):
    ...
    pagination_class = CustomBlogResultsSetPagination
```


## Cursor Pagination

Editar `settings.py`


```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 5
}
```

> Requer um campo com o nome `created` no seu modelo.

