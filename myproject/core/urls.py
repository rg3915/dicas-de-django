from django.urls import path
from myproject.core import views as v


app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.person_list, name='person_list'),
    path('articles/', v.article_list, name='article_list'),
    path('articles/filter/', v.article_filter_list, name='article_filter_list'),
    path('articles/json/', v.article_json, name='article_json'),
]
