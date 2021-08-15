# 43 - django-admin-rangefilter

https://github.com/silentsokolov/django-admin-rangefilter

```
pip install django-admin-rangefilter
```

Em `settings.py`


```python
INSTALLED_APPS = [
    ...
    'rangefilter',
    ...
]
```

Em `core/admin.py`
￼
```python
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_filter = (
        ('published_date', DateRangeFilter),
        ('modified', DateTimeRangeFilter),
    )
```
