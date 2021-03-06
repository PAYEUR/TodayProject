from django.conf.urls import url

from . import views

app_name = 'connection'
urlpatterns = [
    url(r'^login$', views.connexion, name='login'),
    url(r'^logout$', views.deconnexion, name='logout'),
    url(r'^inscription$', views.create_user, name='registration'),
    ]
