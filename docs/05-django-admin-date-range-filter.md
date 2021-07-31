# 5 - Django Admin Date Range filter

<a href="https://youtu.be/s5QzePekrvQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

https://github.com/tzulberti/django-datefilterspec

```
pip install django-daterange-filter
```

```python
# settings.py
INSTALLED_APPS = (
    ...
    'daterange_filter'
)
```

```python
# admin.py
from daterange_filter.filter import DateRangeFilter

...

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...
    list_filter = (
        ('published_date', DateRangeFilter),
        'category',
    )
```
