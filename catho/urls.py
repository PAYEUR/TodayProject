from django.conf.urls import url
from django.conf.urls import include



app_name = 'catho'
urlpatterns = [
    url(r'^', include('topic.urls')),
    # url(r'^tableau_de_bord$', views.EventPlannerPanel.as_view(), name="event_planner_panel"),

    # add crud_url under core/gestion/ajouter_evenement for example
    url(r'^gestion/', include('crud.urls')),

    ]

