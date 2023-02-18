from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('accounts/', include('backend.accounts.urls')),  # noqa E501
    path('bookstore/', include('backend.bookstore.urls', namespace='bookstore')),  # noqa E501
    path('crm/', include('backend.crm.urls', namespace='crm')),  # noqa E501
    path('expense/', include('backend.expense.urls', namespace='expense')),  # noqa E501
    path('product/', include('backend.product.urls', namespace='product')),  # noqa E501
    path('todo/', include('backend.todo.urls', namespace='todo')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
