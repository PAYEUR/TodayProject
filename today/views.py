import calendar
import logging


from datetime import datetime, timedelta
from django import http
from django.shortcuts import get_object_or_404, get_list_or_404, render

from dateutil import parser

from . import forms
from forms import EventForm
from .models import Event, EventType, Occurrence

from . import swingtime_settings

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


# TODO build a context processor to get event.label for navbar
# nav-bar functions to call in each context

def nav_bar():
    return {'nav_list':  get_list_or_404(EventType)}


# today's views
# -------------------------------------------------------------------------------

def index(request):
    context = nav_bar()
    return render(request, 'today/home.html', context)



def get_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    context = dict({'event': event}
                   , **nav_bar())
    return render(request, 'today/single_event.html', context)


def _events_in_a_period(request, days, template='today/event_by_date.html'):
    """

    :param request:
    :param days: a list of days
    :return: context with occurrences, event_types_list and days
    """
    # not satisfying because len(moment) times database requests
    # print all occurrences
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    # get all related event_types  (double sorted)
    events_list = [occurrence.event for occurrence in occurrences]
    event_types_list = list(set([event.event_type for event in events_list]))
                                 # list(set([occurrence.event for occurrence in occurrences]))]))



    context = dict({'occurrences': occurrences,
                   'event_types_list' : event_types_list,
                    'days': days,
                    },  **nav_bar())

    return render(request, template, context)


def today_events(request, template='today/event_by_date.html'):
    """

    :param request:
    :param template:
    :return: all events for today
    """
    days = [datetime.now()]
    return _events_in_a_period(request, days, template)


def tomorrow_events(request, template='today/event_by_date.html'):
    """

    :param request:
    :param template:
    :return: all events for tomorrow
    """
    days = [datetime.now()+timedelta(days=+1)]
    return _events_in_a_period(request, days, template)


def coming_days_events(request,next_days_duration=7, template='today/event_by_date.html'):
    """

    :param request:
    :param next_days_duration: how many days does "coming_days" mean
    :param template:
    :return: all events for coming_days
    """
    today = datetime.now()
    i =0
    days = []
    while i < int(next_days_duration):
        days.append(today +timedelta(days=+i))
        i+=1

    return _events_in_a_period(request, days, template)


def daily_events(request, year, month, day, template='today/event_by_date.html'):

    days = [datetime(int(year), int(month), int(day))]

    return _events_in_a_period(request, days, template)


def monthly_events(request, year, month, template='today/event_by_date.html'):

    year, month = int(year), int(month)
    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(year, month)
    days=[]
    for week in weeks:
        for day in week:
            days.append(day)

    return _events_in_a_period(request, days, template)




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
def occurrence_view(
    request,
    event_pk,
    pk,
    template='swingtime/occurrence_detail.html',
    form_class=forms.SingleOccurrenceForm
    ):
    """
    View a specific occurrence and optionally handle any updates.

    Context parameters:

    ``occurrence``
        the occurrence object keyed by ``pk``

    ``form``
        a form object for updating the occurrence
    """
    occurrence = get_object_or_404(Occurrence, pk=pk, event__pk=event_pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=occurrence)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(request.path)
    else:
        form = form_class(instance=occurrence)

    return render(request, template, {'occurrence': occurrence, 'form': form})


#-------------------------------------------------------------------------------
def add_event(
    request,
    template='today/add_event.html',
    event_form_class=EventForm,
    recurrence_form_class=forms.MultipleOccurrenceForm
    ):
    """
    Add a new ``Event`` instance and 1 or more associated ``Occurrence``s.

    Context parameters:

    ``dtstart``
        a datetime.datetime object representing the GET request value if present,
        otherwise None

    ``event_form``
        a form object for updating the event

    ``recurrence_form``
        a form object for adding occurrences

    """
    global supp_context
    dtstart = None
    if request.method == 'POST':
        event_form = event_form_class(request.POST, request.FILES)
        recurrence_form = recurrence_form_class(request.POST)
        if event_form.is_valid() and recurrence_form.is_valid():
            event = event_form.save()
            recurrence_form.save(event)
            return http.HttpResponseRedirect(event.get_absolute_url())

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class()
        recurrence_form = recurrence_form_class(initial={'dtstart': dtstart})

    context = dict({'dtstart': dtstart, 'event_form': event_form, 'recurrence_form': recurrence_form}
                   , **nav_bar())

    return render(request, template, context)
