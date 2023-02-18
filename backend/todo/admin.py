from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'done')
    search_fields = ('task',)
    list_filter = ('done',)
