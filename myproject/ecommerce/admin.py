from django.contrib import admin

from .models import Order, OrderItems

admin.site.register(Order)


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity', 'price')
