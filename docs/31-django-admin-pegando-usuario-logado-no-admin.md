# 31 - Django Admin: Pegando usuário logado no Admin

<a href="https://youtu.be/qP5-ZICzHyM">
    <img src="../.gitbook/assets/youtube.png">
</a>

Em `models.py` considere

```python
# models.py
from django.contrib.auth.models import User


class Article(models.Model):
    ...
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
```

E em `admin.py`

```python
# admin.py
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.save()
        super(ArticleAdmin, self).save_model(request, obj, form, change)
```
