from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.today_events, name="index"),
    url(r'^evenement(?P<event_id>[0-9]+)$', views.get_event, name="get_event"),
    url(r'^nouvel_evenement$', views.add_event,  # {'recurrence_form_class': SingleOccurrenceForm},
        name="nouvel_evenement"),
    url(r'^evenements/aujourd-hui/$', views.today_events, name="today_events"),
    url(r'^evenements/demain/$', views.tomorrow_events, name="tomorrow_events"),
    url(r'^evenements/prochains-jours/$', views.coming_days_events, name="coming_days_events"),
    url(r'^evenements/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/(?P<day>[0-3]?\d)/$', views.daily_events,
        name="daily_events"),
    url(r'^evenements/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/$', views.monthly_events,
        name="monthly_view"),
    ]
