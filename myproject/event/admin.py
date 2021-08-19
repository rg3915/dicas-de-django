from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_participants', 'num_chairs')
    search_fields = ('name',)
