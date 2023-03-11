# product/admin.py
from django.contrib import admin

from .models import Category, Photo, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('title',)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (PhotoInline,)
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    search_fields = ('title',)
    list_filter = ('category',)
    # date_hierarchy = 'created'
