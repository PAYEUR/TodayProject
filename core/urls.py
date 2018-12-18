from django.conf.urls import url

from .views import *
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from topic.models import Occurrence

sitemap_dict = {
    'queryset': Occurrence.objects.all(),
    'date_field': 'start_time',
}


app_name = 'core'
urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'enjoytoday': GenericSitemap(sitemap_dict, priority=0.6)}},
        name='django.contrib.sitemaps.views.sitemap'),
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
    ]
