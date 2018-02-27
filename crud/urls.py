from django.conf.urls import url

from . import views
from test import test_views

app_name = 'crud'
urlpatterns = [
    url(r'^nouvel_evenement', views.add_event, name="create_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/modifier$', views.UpdateEvent.as_view(), name="update_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/supprimer$', views.DeleteEvent.as_view(), name="delete_event"),
    #url(r'^evenement(?P<event_id>[0-9]+)/ajouter_occurrences$', views.add_occurrences, name="add_occurrences"),
    url(r'^modifier_occurrence(?P<occurrence_id>[0-9]+)$', views.UpdateOccurrence.as_view(), name="update_occurrence"),
    url(r'^supprimer_occurrence(?P<occurrence_id>[0-9]+)$', views.DeleteOccurrence.as_view(), name="delete_occurrence"),

    url(r'^test_add$', test_views.add_event_test2, name="test4"),
url(r'^two_event_types_test$', test_views.two_event_types_test, name="test1"),
    ]
