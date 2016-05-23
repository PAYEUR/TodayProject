from django.conf.urls import url

from .views import ContactView, EventPlannerPanelView

# here is the main application:
# we arrive on it whether coming from enjoytoday or from paris.enjoytoday
## index let us choose which topic we do want (catho, jobs, etc...)
## contact give the main information about enjoytoday team
## event_planner_pannel does not depends on city nor core

app_name = 'core'
urlpatterns = [
    # url(r'^$', views.index, name="index"),
    url(r'^contact$', ContactView.as_view(), name="contact"),
    url(r'^tableau_de_bord$', EventPlannerPanelView.as_view(), name="event_planner_panel"),

    ]

