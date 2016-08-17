# coding="utf-8"
from crud import urls as crud_urls
from django.conf.urls import url, include
from . import views


app_name = 'topic'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^evenement(?P<pk>[0-9]+)$', views.OccurrenceDetail.as_view(), name="get_occurrence"),
    url(r'^toutes-categories/aujourd-hui/$', views.today_events, name="today_events"),
    url(r'^toutes-categories/demain/$', views.tomorrow_events, name="tomorrow_events"),
    url(r'^toutes-categories/prochains-jours/$', views.coming_days_events, name="coming_days_events"),

    url(r'^categorie(?P<event_type_id_string>.+)/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$',
        views.single_day_event_type_list, name="single_day_event_type_list"),

    url(r'^categorie(?P<event_type_id_string>.+)/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/(?P<start_hour_string>.+)-(?P<end_hour_string>.+)$',
        views.single_time_event_type_list, name="single_time_event_type_list"),

    # this one is not really usefull
    url(r'^toutes-categories/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$', views.daily_events,
        name="daily_events"),
    # neither this one as event_type_string has been created
    url(r'^categorie(?P<event_type_id_string>[0-9]+)/$', views.event_type_coming_days, name="event_type_coming_days"),

    # add crud_url under catho/ajouter_evenement for example
    url(r'^', include(crud_urls, namespace='crud')),


    ]
