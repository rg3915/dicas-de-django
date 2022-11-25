from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
