from django.urls import path

from myproject.ecommerce import views as v

app_name = 'ecommerce'


urlpatterns = [
    path('create/', v.order_create, name='order_create'),
    path('add-row/', v.add_row, name='add_row'),
    path('product/price/', v.product_price, name='product_price'),
    path('order/<int:pk>/result/', v.order_result, name='order_result'),
]
