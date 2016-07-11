from django.views.generic import ListView, TemplateView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from topic.models import Event
from connection.models import EnjoyTodayUser

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# core's views
# -------------------------------------------------------------------------------

class IndexView(TemplateView):
    template_name = 'core/index.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class EventPlannerPanelView(LoginRequiredMixin, ListView):

    # mixin parameters
    login_url = 'connection:login'

    ## view parameters
    model = Event
    context_object_name = 'events'
    template_name = 'core/event_planner_panel.html'

    def get_event_planner(self):
        return EnjoyTodayUser.objects.get(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(event_planner=self.get_event_planner())

    def get_context_data(self, **kwargs):
        context = super(EventPlannerPanelView, self).get_context_data(**kwargs)
        context['event_planner'] = self.get_event_planner()

        return context


class NewEventView(TemplateView):
    template_name = 'core/add_event_topic.html'
