# bookstore/admin.py
from django.contrib import admin

from .models import Customer, Ordered


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'active')
    search_fields = ('first_name', 'last_name')
    list_filter = ('active',)


@admin.register(Ordered)
class OrderedAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'status')
    search_fields = (
        'customer__first_name',
        'customer__last_name',
        'customer__email',
    )
    list_filter = ('status',)
    date_hierarchy = 'created'
