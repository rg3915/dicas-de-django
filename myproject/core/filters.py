import django_filters

from .models import Article


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    subtitle = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ('title', 'subtitle')
