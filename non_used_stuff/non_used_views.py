import calendar
import logging


from datetime import datetime, timedelta
from django import http
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect

from dateutil import parser

from topic import forms
from topic.forms import EventForm, IndexForm
# from . import models
from topic.models import Event, EventType, Occurrence

from topic import swingtime_settings

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)

# swingtime's views
# -------------------------------------------------------------------------------
def event_listing(
    request,
    template='swingtime/event_list.html',
    events=None,
    **extra_context
    ):
    """
    View all ``events``.

    If ``events`` is a queryset, clone it. If ``None`` default to all ``Event``s.

    Context parameters:

    ``events``
        an iterable of ``Event`` objects

    ... plus all values passed in via **extra_context
    """
    if events is None:
        events = Event.objects.all()

    extra_context['events'] = events
    return render(request, template, extra_context)


#-------------------------------------------------------------------------------
def event_view(
    request,
    pk,
    template='swingtime/event_detail.html',
    event_form_class=EventForm,
    recurrence_form_class=forms.MultipleOccurrenceForm
    ):
    """
    View an ``Event`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    ``event``
        the event keyed by ``pk``

    ``event_form``
        a form object for updating the event

    ``recurrence_form``
        a form object for adding occurrences
    """
    event = get_object_or_404(Event, pk=pk)
    event_form = recurrence_form = None
    if request.method == 'POST':
        if '_update' in request.POST:
            event_form = event_form_class(request.POST, instance=event)
            if event_form.is_valid():
                event_form.save(event)
                return http.HttpResponseRedirect(request.path)
        elif '_add' in request.POST:
            recurrence_form = recurrence_form_class(request.POST)
            if recurrence_form.is_valid():
                recurrence_form.save(event)
                return http.HttpResponseRedirect(request.path)
        else:
            return http.HttpResponseBadRequest('Bad Request')

    data = {
        'event': event,
        'event_form': event_form or event_form_class(instance=event),
        'recurrence_form': recurrence_form or recurrence_form_class(initial={'dtstart': datetime.now()})
    }
    return render(request, template, data)


#-------------------------------------------------------------------------------
# def occurrence_view(
#     request,
#    event_pk,
#    pk,
#    template='swingtime/occurrence_detail.html',
#    form_class=forms.SingleOccurrenceForm
#    ):
#    """
#    View a specific occurrence and optionally handle any updates.
#
#    Context parameters:
#
#    ``occurrence``
#        the occurrence object keyed by ``pk``
#
#    ``form``
#        a form object for updating the occurrence
#    """
#    occurrence = get_object_or_404(Occurrence, pk=pk, event__pk=event_pk)
#    if request.method == 'POST':
#        form = form_class(request.POST, instance=occurrence)
#        if form.is_valid():
#            form.save()
#            return http.HttpResponseRedirect(request.path)
#    else:
#        form = form_class(instance=occurrence)
#
#    return render(request, template, {'occurrence': occurrence, 'form': form})
#
#
#-------------------------------------------------------------------------------


# not for now
# research view, after http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
# def search(request):
#    """
#    :param request:
#    :return: events corresponding to search terms. Only events, no dates.
#    """
#    query_string =''
#    found_entries = None
#    if ('q' in request.GET) and request.GET['q'].strip():
#        query_string = request.GET['q']
#        # query on Event.city.city_name, Event
#        entry_query = models.get_query(query_string, ['city__city_name', 'description', 'event_type__label'])
#        events = Event.objects.filter(entry_query)
#
#    return redirect("eventlist", object_list=events)
#
#
#class EventList(ListView):
#    model = Event
#    template_name = "event_list.html"
#
#    def get_context_data(self, **kwargs):
#        context = super(EventList,self).get_context_data(**kwargs)
#        context['nav_list'] = get_list_or_404(EventType)
#        return context

