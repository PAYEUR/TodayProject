from django.contrib import admin
from .models import Topic, Event, EventType, Occurrence


class EventAdmin(admin.ModelAdmin):

    list_display = ('title',
                    'address',
                    'location',
                    'event_type',
                    'event_planner',
                    'created_at',
                    )

    list_filter = ['location', 'event_type']


class OccurrenceAdmin(admin.ModelAdmin):

    list_display = ('start_time',
                    'end_time',
                    'event',
                    'is_multiple',
                    )

admin.site.register(EventType)
admin.site.register(Event, EventAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Topic)
