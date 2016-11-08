from django.contrib import admin
from .models import Topic
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin

SiteAdmin.list_display = ('id', 'domain', 'name')

admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
admin.site.register(Topic)