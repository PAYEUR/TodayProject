from django.conf.urls import url

from . import views
from test import test_views

app_name = 'crud'
urlpatterns = [
    # tests
    url(r'^two_event_types_test$', test_views.two_event_types_test, name="two_event_type_test"),
    url(r'^occurrences_test$', test_views.occurrences_test, name="occurrences_test"),
    url(r'^test_add$', views.add_event2, name="add_event2"),

    url(r'^nouvel_evenement_multiple$', views.add_multiple_occurrence_event, name="nouvel_evenement_multiple"),
    url(r'^nouvel_evenement_simple$', views.add_single_event, name="nouvel_evenement_simple"),
    url(r'^nouvel_evenement_par_dates$', views.add_multiple_dates, name="add_multiple_dates"),
    url(r'^evenement(?P<event_id>[0-9]+)/modifier$', views.UpdateEvent.as_view(), name="update_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/supprimer$', views.DeleteEvent.as_view(), name="delete_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/ajouter_occurrences$', views.add_multiples_occurrences, name="add_multiples_occurrences"),
    url(r'^modifier_echeance(?P<occurrence_id>[0-9]+)$', views.UpdateOccurrence.as_view(), name="update_occurrence"),
    url(r'^supprimer_echeance(?P<occurrence_id>[0-9]+)$', views.DeleteOccurrence.as_view(), name="delete_occurrence"),
    ]
