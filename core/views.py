from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from topic.models import Event
from connection.models import EventPlanner
# from .models import Topic


# core's views
# -------------------------------------------------------------------------------
class ContactView(TemplateView):
    template_name = 'core/contact.html'


class IndexView(ListView):
    # return a list of cities and topics
    template_name = ''


class SecondIndexView(ListView):
    # return a list of topics for one single city.
    template_name = ''


class EventPlannerPanel(LoginRequiredMixin, ListView):

    # mixin parameters
    login_url = 'connection:login'

    ## view parameters
    model = Event
    context_object_name = 'events'
    template_name = 'core/event_planner_panel.html'

    def get_event_planner(self):
        return EventPlanner.objects.get(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(event_planner=self.get_event_planner())

    def get_context_data(self, **kwargs):
        context = super(EventPlannerPanel, self).get_context_data(**kwargs)
        context['event_planner'] = self.get_event_planner()

        return context
