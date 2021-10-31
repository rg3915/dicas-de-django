# 53 - DRF: Criando subrota com action

<a href="">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing)

Doc: [https://www.django-rest-framework.org/api-guide/routers/#routing-for-extra-actions](https://www.django-rest-framework.org/api-guide/routers/#routing-for-extra-actions)


Editar `blog/models.py`

```python
class Post(models.Model):
    ...
    like = models.BooleanField(null=True)
```

Editar `blog/views.py`

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

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

Editar `blog/admin.py`

```python
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_by', 'like')
    list_filter = ('like',)
```

As novas rotas são:

```
/blog/posts/<pk>/like/
/blog/posts/<pk>/unlike/
/blog/posts/my_posts/
```
