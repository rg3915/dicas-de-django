# 39 - Django Admin: display decorator (Django 3.2+)

<a href="https://youtu.be/lKEPuwBjHss">
    <img src="../.gitbook/assets/youtube.png">
</a>

https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator

**IMPORTANTE:** Usei um [boilerplate](https://github.com/rg3915/dicas-de-django#11---django-boilerplate) para mostrar essa feature num projeto separado. Assista o video no YouTube.

O Django 3.2+ tem uma feature chamada `display` decorator.

Antigamente você fazia `short_description` assim:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date')

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

... e ainda funciona.

Mas a partir do Django 3.2+ você pode usar o `display` decorator.

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date', 'is_published')

    # Django 3.2+
    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```
