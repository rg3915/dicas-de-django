# bookstore/admin.py
from django.contrib import admin

from .models import Author, Book, Customer, Ordered, Publisher, Sale, Store


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


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'paid', 'date_paid', 'method', 'deadline')
    list_filter = ('paid', 'method')
    date_hierarchy = 'created'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('first_name', 'last_name')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'isbn',
        '__str__',
        'rating',
        'price',
        'stock_min',
        'stock',
        'publisher',
    )
    list_display_links = ('__str__',)
    search_fields = ('isbn', 'title')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('name',)
