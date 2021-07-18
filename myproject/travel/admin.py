from django.contrib import admin

from .models import Travel


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = (
        'destination',
        'date_travel',
        'datetime_travel',
        'time_travel',
        'duration_travel',
    )
    search_fields = ('destination',)
