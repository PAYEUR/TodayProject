from django.conf.urls import url

from . import views
from swingtime.forms import SingleOccurrenceForm

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^base$', views.EventTypeWithImageView.as_view(), name="base"),
    url(r'^evenement(?P<event_id>[0-9]+)$', views.get_event, name="get_event"),
    url(r'^calendar/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$', views.get_event_by_date, name="daily_view"),
    url(r'^nouvel_evenement$', views.add_event, # {'recurrence_form_class': SingleOccurrenceForm},
        name="nouvel_evenement" ),
    ]