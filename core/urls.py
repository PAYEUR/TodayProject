from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from .views import *
from sitemaps import sitemaps


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
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps()}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="core/robots.txt", content_type='text/plain')),

    ]
