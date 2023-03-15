# product/urls.py
from django.urls import include, path

from backend.product import views as v

app_name = 'product'

# A ordem das urls é importante por causa do slug, quando existir.
product_patterns = [
    # path('', v.ProductListView.as_view(), name='product_list'),  # noqa E501
    path('', v.product_list, name='product_list'),  # noqa E501
    path('create/', v.product_create, name='product_create'),  # noqa E501
    path('<int:pk>/', v.product_detail, name='product_detail'),  # noqa E501
    path('<int:pk>/update/', v.product_update, name='product_update'),  # noqa E501
    path('<int:pk>/delete/', v.product_delete, name='product_delete'),  # noqa E501
    path('import/', v.import_view, name='import_view'),  # noqa E501
    path('export/csv/', v.export_csv, name='export_csv'),  # noqa E501
    path('export/xlsx/', v.export_xlsx, name='export_xlsx'),  # noqa E501
]

urlpatterns = [
    path('', include(product_patterns)),
]
