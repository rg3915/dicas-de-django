from django.urls import path

from myproject.travel import views as v

app_name = 'travel'


urlpatterns = [
    path('', v.TravelListView.as_view(), name='travel_list'),
    path('create/', v.TravelCreateView.as_view(), name='travel_create'),
]
