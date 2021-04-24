import json
from dateutil.parser import parse
from datetime import timedelta
from pprint import pprint
from django.http import JsonResponse
from django.shortcuts import render
from .models import Article
from .filters import ArticleFilter


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


def person_list(request):
    template_name = 'core/person_list.html'
    return render(request, template_name)


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Converte em data e adiciona um dia.
        # end_date = parse(end_date) + timedelta(1)
        # Usando date antes de range não precisa do timedelta.
        object_list = object_list.filter(
            published_date__date__range=[start_date, end_date]
        )

    context = {'object_list': object_list, 'model': Article}
    return render(request, template_name, context)


def article_filter_list(request):
    template_name = 'core/article_filters_list.html'
    object_list = Article.objects.all()
    article_list = ArticleFilter(request.GET, queryset=object_list)

    context = {
        'object_list': object_list,
        'filter': article_list
    }
    return render(request, template_name, context)


def article_json(request):
    text = '''
    {
        "title": "JSON",
        "subtitle": "Entendento JSON dumps e loads",
        "slug": "entendento-json-dumps-e-loads",
        "value": "42"
    }
    '''
    data = json.loads(text)
    pprint(data)
    print(type(data))
    print(data['value'], 'is', type(data['value']))

    data['title'] = 'Introdução ao JSON'
    data['value'] = int(data['value']) + 1
    data['pi'] = 3.14
    data['active'] = True
    data['nulo'] = None
    return JsonResponse(data)
