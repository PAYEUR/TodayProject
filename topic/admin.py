from django.contrib import admin
from .models import Event, EventType, Occurrence

class EventAdmin(admin.ModelAdmin):

    list_display = ('title',
                    'address',
                    'site',
                    'event_type',
                    'event_planner',
                    )

    list_filter = ['site', 'event_type']

admin.site.register(EventType)
admin.site.register(Event, EventAdmin)
admin.site.register(Occurrence)
