from django.conf.urls import url

import views

app_name = 'crud'
urlpatterns = [
    url(r'^nouvel_evenement', views.add_event_and_occurrences, name="create_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/modifier$', views.update_event, name="update_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/supprimer$', views.DeleteEvent.as_view(), name="delete_event"),
    # url(r'^evenement(?P<event_id>[0-9]+)/ajouter_occurrences$', views.add_occurrences, name="add_occurrences"),
    url(r'^modifier_occurrence(?P<occurrence_id>[0-9]+)$', views.UpdateOccurrence.as_view(), name="update_occurrence"),
    url(r'^supprimer_occurrence(?P<occurrence_id>[0-9]+)$', views.DeleteOccurrence.as_view(), name="delete_occurrence"),
    url(r'^tableau-de-bord$', views.EventPlannerPanelView.as_view(), name="event_planner_panel"),

    ]
