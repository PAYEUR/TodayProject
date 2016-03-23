from django.contrib import admin
from .models import Event, EventType, City, Occurrence, EventPlanner

admin.site.register(EventType)
admin.site.register(City)
admin.site.register(Event)
admin.site.register(Occurrence)
admin.site.register(EventPlanner)