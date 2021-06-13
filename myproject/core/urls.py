from django.urls import path

from myproject.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.PersonListView.as_view(), name='person_list'),
    path('persons/create/', v.person_create, name='person_create'),
    path('articles/', v.article_list, name='article_list'),
    path('articles/filter/', v.article_filter_list, name='article_filter_list'),
    path('articles/json/', v.article_json, name='article_json'),
]
