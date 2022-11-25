from django.urls import path

from backend.crm import views as v

app_name = 'crm'


urlpatterns = [
    path('contact/', v.send_contact, name='send_contact'),  # noqa E501
]
