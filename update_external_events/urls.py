# coding="utf-8"
from django.conf.urls import url
import views


app_name = 'update_external_events'
urlpatterns = [
    url(r'^update-events', views.update_external_events, name="update_external_events"),
    ]
