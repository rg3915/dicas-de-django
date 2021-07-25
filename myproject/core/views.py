import json
from pprint import pprint

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView

from .filters import ArticleFilter
from .forms import PersonForm
from .models import Article, Person


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PersonListView, self).get_queryset()

        data = self.request.GET
        search = data.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(bio__icontains=search)
            )

        return queryset


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


def person_create(request):
    template_name = 'core/person_form.html'
    # Não esquecer do request.user como primeiro parâmetro.
    form = PersonForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('person:person_list')

    context = {'form': form}
    return render(request, template_name, context)
