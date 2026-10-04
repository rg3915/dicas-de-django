# Dica 53 - DRF: Criando subrota com action

**Versões usadas no vídeo:** Django 3.2.7, Django REST framework 3.12, drf-yasg 1.20 e Python 3.9.
{: .versoes }

<a href="https://youtu.be/6IS8KfzvD74">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing)

Doc: [https://www.django-rest-framework.org/api-guide/routers/#routing-for-extra-actions](https://www.django-rest-framework.org/api-guide/routers/#routing-for-extra-actions)

Continuando a série sobre Django REST framework, vamos ver como criar uma **subrota** que executa uma ação extra num ViewSet, usando o decorator `@action`. O objetivo: dar **like** e **unlike** num post do blog e ter uma rota que retorna **somente os meus posts**.

## Pré-requisitos

* O projeto `drf-example` das dicas anteriores, com a app `blog` e o `PostViewSet` da [Dica 52](052-drf-django-filter.md) (o `Post` tem o campo `created_by`, ligado ao usuário que criou o post).
* O django-extensions (para o `show_urls`) e o drf-yasg (para testar pelo Swagger), instalados nas dicas anteriores.

## O campo like

Editar `blog/models.py`

Acrescente um `BooleanField` chamado `like`, com `null=True`: assim ele tem três estados, desconhecido (nulo), like (`True`) e unlike (`False`).

```python
# blog/models.py
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
    like = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title
```

Editar `blog/admin.py`

Mostre o `like` na lista do Admin e acrescente um filtro por ele:

```python
# blog/admin.py
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_by', 'like')
    list_filter = ('like',)
```

Rode as migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Migrations for 'blog':
  blog/migrations/0004_post_like.py
    - Add field like to post
```

No Admin, em Blog > Posts, aparece a coluna **Like** de cada post (no início, todos como desconhecido).

## Like com @action

Editar `blog/views.py`

Importe o `action` e o `Response`:

```python
# blog/views.py
from rest_framework.decorators import action
from rest_framework.response import Response
```

O `filterset_class` da dica anterior foi comentado, para não atrapalhar. E crie o método `like` dentro do `PostViewSet`, decorado com `@action`:

```python
# blog/views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    # filterset_class = PostFilter

    @action(detail=True, methods=['put'])
    def like(self, request, pk=None):
        '''
        Marca Like = True
        '''
        post_obj = self.get_object()
        post_obj.like = True
        post_obj.save()
        serializer = self.get_serializer(post_obj)
        return Response(serializer.data)
```

Os dois parâmetros do `@action` são importantes:

* `detail`: com `detail=True` a ação é sobre **um** objeto, e a rota leva o `pk` (`/blog/posts/<pk>/like/`); com `detail=False` ela é sobre a **lista** (`/blog/posts/my_posts/`, mais abaixo).
* `methods`: os métodos HTTP aceitos; aqui, `put`.

Dentro do método:

* `self.get_object()` pega o post do `pk` da URL (o nome `post_obj` é só para não confundir com o model `Post`);
* marca `like = True` e salva;
* serializa de novo com `self.get_serializer` e devolve o resultado com `Response`.

E a rota? Você não precisa criar: o router faz isso automaticamente para cada `@action`. Para conferir, use o `show_urls` do django-extensions:

```bash
python manage.py show_urls
```

```
/blog/posts/<pk>/like/    blog.views.PostViewSet    Post-like
/blog/posts/<pk>/like\.<format>/    blog.views.PostViewSet    Post-like
```

Rode o servidor e abra o Swagger em `http://localhost:8000/swagger/`:

```bash
python manage.py runserver
```

Aparece a rota `PUT /blog/posts/{id}/like/`, com a descrição "Marca Like = True" (tirada da docstring). Clique em **Try it out**, informe o `id` de um post (no vídeo, `397`) e clique em **Execute**. O post volta com `"like": true`, e no Admin ele deixa de aparecer como desconhecido.

## Unlike

O unlike é a mesma coisa, com `False`:

```python
# blog/views.py
    @action(detail=True, methods=['put'])
    def unlike(self, request, pk=None):
        '''
        Marca Like = False
        '''
        post_obj = self.get_object()
        post_obj.like = False
        post_obj.save()
        serializer = self.get_serializer(post_obj)
        return Response(serializer.data)
```

Reinicie o servidor, e no Swagger aparece também `PUT /blog/posts/{id}/unlike/`. As duas subrotas foram criadas automaticamente.

## Retornando somente os meus posts (detail=False)

Agora uma ação sobre a lista, com `detail=False` e só o método `get`: ela retorna somente os posts do usuário logado.

```python
# blog/views.py
    @action(detail=False, methods=['get'])
    def my_posts(self, request, pk=None):
        '''
        Retorna somente os meus posts.
        '''
        user = self.request.user
        # posts = Post.objects.filter(created_by=user)
        posts = self.get_queryset().filter(created_by=user)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
```

* `self.request.user` é o usuário logado (por isso a view exige `IsAuthenticated`).
* `self.get_queryset()` devolve o `queryset` da view, e filtramos por `created_by=user`, como na dica anterior.
* Se a paginação estiver configurada, `self.paginate_queryset` devolve a página, e a resposta sai paginada com `self.get_paginated_response`. Senão, serializamos tudo com `many=True` e devolvemos com `Response`.

## views.py completo

```python
# blog/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

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
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    # filterset_class = PostFilter

    @action(detail=True, methods=['put'])
    def like(self, request, pk=None):
        '''
        Marca Like = True
        '''
        post_obj = self.get_object()
        post_obj.like = True
        post_obj.save()
        serializer = self.get_serializer(post_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def unlike(self, request, pk=None):
        '''
        Marca Like = False
        '''
        post_obj = self.get_object()
        post_obj.like = False
        post_obj.save()
        serializer = self.get_serializer(post_obj)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request, pk=None):
        '''
        Retorna somente os meus posts.
        '''
        user = self.request.user
        # posts = Post.objects.filter(created_by=user)
        posts = self.get_queryset().filter(created_by=user)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
```

## As novas rotas

As novas rotas são:

```
/blog/posts/<pk>/like/
/blog/posts/<pk>/unlike/
/blog/posts/my_posts/
```

Saída do `show_urls` filtrada para os posts:

```
/blog/posts/                        blog.views.PostViewSet  Post-list
/blog/posts/<pk>/                   blog.views.PostViewSet  Post-detail
/blog/posts/<pk>/like/              blog.views.PostViewSet  Post-like
/blog/posts/<pk>/unlike/            blog.views.PostViewSet  Post-unlike
/blog/posts/my_posts/               blog.views.PostViewSet  Post-my-posts
```

No Swagger, `GET /blog/posts/my_posts/` (com o parâmetro `page`, porque a paginação está ativa) devolve somente os posts do usuário logado; no vídeo, os do usuário `regis`.

Com o `@action` você cria ações extras num ViewSet, sobre um objeto (`detail=True`) ou sobre a lista (`detail=False`), e o router cuida das rotas.
