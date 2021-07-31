# 4 - Django Admin personalizado

<a href="https://youtu.be/jogkxIkCzI8">
    <img src="../.gitbook/assets/youtube.png">
</a>

https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-options

#### admin.py

```python
from django.conf import settings
from django.contrib import admin

from .models import Article, Category

# from .forms import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_published_date')
    search_fields = ('title',)
    list_filter = (
        'category',
    )
    readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```
