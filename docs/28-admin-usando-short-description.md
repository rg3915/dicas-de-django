# 28 - Admin: Usando short description

<a href="https://youtu.be/Uwwr77SR8EE">
    <img src="../.gitbook/assets/youtube.png">
</a>


Quando não conseguimos usar o `dunder` no `list_display` do admin, então usamos o `short_description`.


```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'get_published_date', 'get_category')
    ...

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'

    def get_category(self, obj):
        if obj.category:
            return obj.category.title

    get_category.short_description = 'Categoria'
```
