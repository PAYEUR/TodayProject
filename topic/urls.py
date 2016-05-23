# coding="utf-8"
from crud import urls as crud_urls
from django.conf.urls import url, include
from . import views


app_name = 'topic'
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
    url(r'^nouvel_evenement$', views.new_event, name="nouvel_evenement"),
    # add crud_url under core/gestion/ajouter_evenement for example
    url(r'^gestion/', include(crud_urls, namespace='crud')),

    ]

