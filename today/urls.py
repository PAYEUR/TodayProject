from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^base$', views.base, name="base"),
    url(r'^base2$', views.base2, name="base2"),
    url(r'^inscription$', views.get_name, name="get_name"),
    url(r'^evenement$', views.get_event, name="get_event")
    ]
