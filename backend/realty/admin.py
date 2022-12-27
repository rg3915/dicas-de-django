# realty/admin.py
from django.contrib import admin

from .models import PropertyRent, PropertySale


@admin.register(PropertyRent)
class PropertyRentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type_of_negotiation', 'price')
    search_fields = ('name',)
    list_filter = ('type_of_negotiation',)


@admin.register(PropertySale)
class PropertySaleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type_of_negotiation', 'price')
    search_fields = ('name',)
    list_filter = ('type_of_negotiation',)
