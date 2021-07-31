# 29 - Django Admin: Criando actions no Admin

<a href="https://youtu.be/WofnItMvqKU">
    <img src="../.gitbook/assets/youtube.png">
</a>

https://docs.djangoproject.com/en/3.1/ref/contrib/admin/actions/

Em `models.py` considere

```python
# models.py
STATUS_CHOICES = (
    ('d', 'Rascunho'),
    ('p', 'Publicado'),
    ('w', 'Retirado'),
)


class Article(models.Model):
    ...
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
```

E em `admin.py`

```python
# admin.py
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...
    actions = ('make_published',)

    def make_published(self, request, queryset):
        count = queryset.update(status='p')

        if count == 1:
            msg = '{} artigo foi publicado.'
        else:
            msg = '{} artigos foram publicados.'

        self.message_user(request, msg.format(count))

    make_published.short_description = "Publicar artigos"
```
