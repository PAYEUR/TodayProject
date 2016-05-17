from django.conf.urls import url

from . import views

app_name = 'connection'
urlpatterns = [
    url(r'^connexion$', views.connexion, name='login'),
    url(r'^deconnexion$', views.deconnexion, name='logout'),
    url(r'^connection_success$', views.logging_success, name='logging_success'),
    url(r'^inscription$', views.create_user, name='registration'),

    ]