from django.conf.urls import url

import views


app_name = 'update_external_events'
urlpatterns = [
    url(r'^$', views.update_external_events, name="update_external_events"),
    ]
