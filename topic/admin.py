from django.contrib import admin
from .models import Topic, Event, EventType, Occurrence


class EventAdmin(admin.ModelAdmin):

    list_display = ('title',
                    'address',
                    'site',
                    'event_type',
                    'event_planner',
                    'created_at',
                    )

    list_filter = ['site', 'event_type']

admin.site.register(EventType)
admin.site.register(Event, EventAdmin)
admin.site.register(Occurrence)
admin.site.register(Topic)
