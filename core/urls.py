from django.conf.urls import url

from .views import *


# here is the main application:
# we arrive on it whether coming from enjoytoday or from paris.enjoytoday
## index let us choose which topic we do want (catho, jobs, etc...)
## contact give the main information about enjoytoday team
## event_planner_pannel does not depends on city nor core

app_name = 'core'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^contact$', ContactView.as_view(), name="contact"),
    url(r'^l-equipe-enjoytoday', TeamView.as_view(), name="team"),
    url(r'^conditions-generales-d-utilisation', CGUView.as_view(), name="CGU"),
    url(r'^charte-utilisation-cookies', CookiesView.as_view(), name="cookies"),
    url(r'^nous-aider', HelpUsView.as_view(), name="help_us"),
    url(r'^tutoriel', TutorialView.as_view(), name="tutorial"),
    url(r'^presentation-du-projet', PresentationView.as_view(), name="presentation"),
    url(r'^charte-post-d-evenement', CharteView.as_view(), name="charte"),
    url(r'^presentation-des-categories', ExplainCategoriesView.as_view(), name="explain_categories"),

    # TODO: rewrite those views
    url(r'^tableau-de-bord$', EventPlannerPanelView.as_view(), name="event_planner_panel"),
    #url(r'^nouvel_evenement$', NewEventView.as_view(), name="new_event"),

    ]
