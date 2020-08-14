from django.shortcuts import render
from .models import Article


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


def person_list(request):
    template_name = 'core/person_list.html'
    return render(request, template_name)


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)
