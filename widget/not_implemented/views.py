from django.views.generic import TemplateView


class NotImplementedView(TemplateView):
    template_name = 'not_implemented.html'

