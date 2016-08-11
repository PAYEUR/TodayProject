# coding="utf-8"
from crud import urls as crud_urls
from django.conf.urls import url, include
from models import EventType
from . import views2 as views


app_name = 'topic'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^evenement(?P<pk>[0-9]+)$', views.OccurrenceDetail.as_view(), name="get_occurrence"),
    url(r'^toutes-categories/aujourd-hui/$', views.today_events, name="today_events"),
    url(r'^toutes-categories/demain/$', views.tomorrow_events, name="tomorrow_events"),
    url(r'^toutes-categories/prochains-jours/$', views.coming_days_events, name="coming_days_events"),

    url(r'^categorie(?P<event_type_id_string>.+)/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$',
         views.single_day_event_type_list, name="single_day_event_type_list"),

    # add crud_url under catho/ajouter_evenement for example
    url(r'^', include(crud_urls, namespace='crud')),

    # url(r'^categorie(?P<event_type_id>[0-9]+)/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$',
         # views.single_day_event_type, name="single_day_event_type"),
    # url(r'^categorie(?P<event_type_id>[0-9]+)/aujourd-hui/$', views.today_event_type, name="today_event_type"),
    # (r'^categorie(?P<event_type_id>[0-9]+)/demain/$', views.tomorrow_event_type, name="tomorrow_event_type"),
    # url(r'^evenements/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/$', views.monthly_events, name="monthly_view"),

    # this one is not really usefull
    url(r'^toutes-categories/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$', views.daily_events,
        name="daily_events"),
    #neither this one as event_type_string has been created
    url(r'^categorie(?P<event_type_id_string>[0-9]+)/$', views.event_type_coming_days, name="event_type_coming_days"),

    ]

