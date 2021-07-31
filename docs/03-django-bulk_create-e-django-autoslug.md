# 3 - Django bulk_create e django-autoslug

<a href="https://youtu.be/Py-AG6S_vJI">
    <img src="../.gitbook/assets/youtube.png">
</a>

### python-slugify

https://pypi.org/project/python-slugify/

```python
from slugify import slugify

text = 'Dicas de Django'
print(slugify(text))
url = f'example.com/{slugify(text)}'
```

#### bulk-create

https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create


#### django-autoslug

https://pypi.org/project/django-autoslug/

```
pip install django-autoslug
```


#### models.py

```python
from autoslug import AutoSlugField
from django.db import models


class Article(models.Model):
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```


#### shell_plus

```python
categories = [
    'dicas',
    'django',
    'python',
]

aux = []

for category in categories:
    obj = Category(title=category)
    aux.append(obj)

Category.objects.bulk_create(aux)


titles = [
    {
        'title': 'Django Boilerplate',
        'subtitle': 'Django Boilerplate',
        'category': 'dicas'
    },
    {
        'title': 'Django extensions',
        'subtitle': 'Django extensions',
        'category': 'dicas'
    },
    {
        'title': 'Django Admin',
        'subtitle': 'Django Admin',
        'category': 'admin'
    },
    {
        'title': 'Django Autoslug',
        'subtitle': 'Django Autoslug',
        'category': 'dicas'
    },
]

aux = []

for title in titles:
    category = Category.objects.filter(title=title['category']).first()
    article = dict(
        title=title['title'],
        subtitle=title['subtitle']
    )
    if category:
        obj = Article(category=category, **article)
    else:
        obj = Article(**article)
    aux.append(obj)

Article.objects.bulk_create(aux)
```
