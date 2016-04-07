from django.conf.urls import url

from . import views
#from django.conf.urls import include, url



urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^evenement(?P<occurrence_id>[0-9]+)$', views.get_occurrence, name="get_occurrence"),
    url(r'^toutes-categories/aujourd-hui/$', views.today_events, name="today_events"),
    url(r'^toutes-categories/demain/$', views.tomorrow_events, name="tomorrow_events"),
    url(r'^toutes-categories/prochains-jours/$', views.coming_days_events, name="coming_days_events"),
    url(r'^toutes-categories/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$', views.daily_events,
        name="daily_events"),
    url(r'^evenements/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/$', views.monthly_events,
        name="monthly_view"),
    url(r'^categorie(?P<event_type_id>[0-9]+)/$', views.event_type_coming_days, name="event_type_coming_days"),
    url(r'^categorie(?P<event_type_id>[0-9]+)/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$',
        views.single_day_event_type, name="single_day_event_type"),
    url(r'^categorie(?P<event_type_id>[0-9]+)/aujourd-hui/$', views.today_event_type, name="today_event_type"),
    url(r'^categorie(?P<event_type_id>[0-9]+)/demain/$', views.tomorrow_event_type, name="tomorrow_event_type"),
    url(r'^contact$', views.contact, name="contact"),
    url(r'^nouvel_evenement_multiple$', views.add_multiple_occurrence_event, name="nouvel_evenement_multiple"),
    url(r'^nouvel_evenement_simple$', views.add_single_event, name="nouvel_evenement_simple"),
    url(r'^nouvel_evenement_par_dates$', views.add_multiple_dates, name="add_multiple_dates"),
    url(r'^nouvel_evenement$', views.new_event, name="nouvel_evenement"),
    url(r'^tableau_de_bord$', views.EventPlannerPanel.as_view(), name="event_planner_panel"),
    url(r'^evenement(?P<event_id>[0-9]+)/modifier$', views.UpdateEvent.as_view(), name="update_event"),
    url(r'^evenement(?P<event_id>[0-9]+)/supprimer$', views.DeleteEvent.as_view(), name="delete_event"),
    url(r'^supprimer_echeance(?P<occurrence_id>[0-9]+)$', views.DeleteOccurrence.as_view(), name="delete_occurrence"),
    url(r'^evenement(?P<event_id>[0-9]+)/ajouter_occurrences$', views.add_multiples_occurrences, name="add_multiples_occurrences"),
    url(r'^connexion$',views.connexion, name='login'),
    url(r'^deconnexion$',views.deconnexion, name='logout'),
    url(r'^connecte$', views.logging_success, name='logging_success'),
    ]
