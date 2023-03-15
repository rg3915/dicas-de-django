# product/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin

from .models import Category, Photo, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('title',)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_classes = [ProductResource]
    inlines = (PhotoInline,)
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    search_fields = ('title',)
    list_filter = ('category',)
    # date_hierarchy = 'created'
