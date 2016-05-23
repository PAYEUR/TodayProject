from django.conf.urls import url, include
from . import views

app_name = 'catho'
urlpatterns = [

    url(r'^truc$', views.truc, name="truc"),

    # add crud_url under core/gestion/ajouter_evenement for example
    #url(r'^gestion/', include('crud.urls')),

    ]

