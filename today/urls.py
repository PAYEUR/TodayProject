from django.conf.urls import url

from . import views
from swingtime.forms import SingleOccurrenceForm

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^base$', views.base, name="base"),
    url(r'^inscription$', views.get_name, name="get_name"),
    url(r'^evenement(?P<event_id>[0-9]+)$', views.get_event, name="get_event"),
    url(r'^nouvel_evenement$', views.set_event, name="set_event"),
    url(r'^event_by$', views.get_event_by, name="get_event_by"),
    url(r'^add_event$', views.add_event, )#{'recurrence_form_class': SingleOccurrenceForm}, name="add_event" ),
    ]
