# coding = utf-8
from django.views.generic import TemplateView


# -----------------------------------------------------------------------------------------
# Generic static views
class IndexView(TemplateView):
    template_name = 'core/index.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class CGUView(TemplateView):
    template_name = 'core/CGU.html'


class TeamView(TemplateView):
    template_name = 'core/team.html'


class HelpUsView(TemplateView):
    template_name = 'core/help_us.html'


class CookiesView(TemplateView):
    template_name = 'core/cookies.html'


class TutorialView(TemplateView):
    template_name = 'core/tutorial.html'


class PresentationView(TemplateView):
    template_name = 'core/presentation_project.html'


class CharteView(TemplateView):
    template_name = 'core/charte_utilisation.html'


class ExplainCategoriesView(TemplateView):
    template_name = 'core/explain_categories.html'
