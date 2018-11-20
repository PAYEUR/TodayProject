"""TodayProject URL Configuration for production environment
"""

from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^update-events/', include('update_external_events.urls')),
    url(r'^', include('core.urls')),
    url(r'^', include('crud.urls')),
    url(r'^connexion/', include('connection.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<city_slug>[\w-]+)/', include('location.urls')),
    ]
