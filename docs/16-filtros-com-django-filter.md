# 16 - Filtros com django-filter

<a href="https://youtu.be/LZJjSeJC09A">
    <img src="../.gitbook/assets/youtube.png">
</a>


Instale o [django-filter](https://django-filter.readthedocs.io/en/stable/)

```
pip install django-filter
```

Acrescente-o ao `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    'django_filters',
]
```

Crie um arquivo `filters.py`

```python
import django_filters

from .models import Article


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    subtitle = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ('title', 'subtitle')
```

Em `views.py`

```python
from .filters import ArticleFilter


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()
    article_filter = ArticleFilter(request.GET, queryset=object_list)

    ...

    context = {
        'object_list': article_filter,
        'filter': article_filter
    }
    return render(request, template_name, context)
```

Em `article_list.html`

```html
  <div class="row">
    <div class="col-md-4">
      <form method="GET">
        {{ filter.form.as_p }}
        <input type="submit" />
      </form>
    </div>

    <div class="col-md-8">
      <table class="table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Sub-título</th>
            <th>Data de publicação</th>
          </tr>
        </thead>
        <tbody>
          {% for obj in filter.qs %}
            <tr>
              <td>{{ obj.title }}</td>
              <td>{{ obj.subtitle }}</td>
              <td>{{ obj.published_date }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
```
