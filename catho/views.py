import calendar
import logging


from datetime import datetime, timedelta
from django import http
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect

from dateutil import parser

from . import forms
from forms import EventForm, IndexForm, SingleOccurrenceForm
from django.forms import formset_factory
from .models import EventType, Occurrence

from . import swingtime_settings

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


# TODO build a context processor to get event.label for navbar
# nav-bar functions to call in each context

def nav_bar():
    return {'nav_list':  get_list_or_404(EventType)}


# catho's views
# -------------------------------------------------------------------------------
def contact(request, template='catho/contact.html'):
    return render(request, template, nav_bar())

def index(request, template='catho/research.html'):
    """
    :param request:
    :param template:
    :return: home template with index form
    """

    if request.method == 'POST':
        form = IndexForm(request.POST)

        if form.is_valid():
            #dont use city from now
            event_type = form.cleaned_data['quoi']
            date = form.cleaned_data['quand']

            if event_type != None:
                return redirect("single_day_event_type",
                                event_type_id=event_type.pk,
                                year=date.year,
                                month=date.month,
                                day=date.day)
            else:
                return redirect("daily_events",
                                year=date.year,
                                month=date.month,
                                day=date.day)

    else:
        form = IndexForm()

    context = dict({'form': form,
                    },  **nav_bar())

    return render(request, template, context)

def get_occurrence(request, occurrence_id):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)

    if occurrence.event.address != "non precise":
        address = occurrence.event.address + ", France"
    else:
        address = False

    context = dict({'occurrence': occurrence,
                    'address': address,
                   }, **nav_bar())
    return render(request, 'catho/single_event.html', context)

def _events_in_a_period(request, days, template='catho/event_by_date.html'):
    """

    :param request:
    :param days: a list of days
    :return: context with occurrences, event_types_list and days
    """
    # not satisfying because len(moment) times database requests

    # print event_types occurrences except multiples occurrences
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day).filter(is_multiple=False)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    # get all related event_types  (double sorted)
    events_list = [occurrence.event for occurrence in occurrences]
    event_types_list = list(set([event.event_type for event in events_list]))

    context = dict({'occurrences': occurrences[:5],
                   'event_types_list' : event_types_list,
                    'days': days,
                    },  **nav_bar())

    return render(request, template, context)


def today_events(request, template='catho/event_by_date.html'):
    """

    :param request:
    :param template:
    :return: all events for catho
    """
    days = [datetime.today()]
    return _events_in_a_period(request, days, template)


def tomorrow_events(request, template='catho/event_by_date.html'):
    """

    :param request:
    :param template:
    :return: all events for tomorrow
    """
    days = [datetime.today()+timedelta(days=+1)]
    return _events_in_a_period(request, days, template)


def coming_days_events(request,next_days_duration=7, template='catho/event_by_date.html'):
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


def daily_events(request, year, month, day, template='catho/event_by_date.html'):

    days = [datetime(int(year), int(month), int(day))]

    return _events_in_a_period(request, days, template)


def monthly_events(request, year, month, template='catho/event_by_date.html'):

    year, month = int(year), int(month)
    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(year, month)
    days=[]
    for week in weeks:
        for day in week:
            days.append(day)

    return _events_in_a_period(request, days, template)


def event_type_coming_days(request, event_type_id, next_days_duration=7,template='catho/date_by_event_type.html'):

    # list of 7 days
    today = datetime.now()
    i =0
    days = []
    while i < int(next_days_duration):
        days.append(today +timedelta(days=+i))
        i+=1

    #sort event_type.occurrences by day
    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day).filter(event__event_type=event_type)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    context = dict({'occurrences': occurrences[:5],
                    'event_type' : event_type,
                    },  **nav_bar())

    return render(request, template, context)


def _single_day_event_type(
        request,
        event_type_id,
        dt,
        template='catho/event_by_date.html'
    ):

    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    occurrences = Occurrence.objects.daily_occurrences(dt=dt).filter(event__event_type=event_type)

    context = dict({'occurrences': occurrences[:5],
                    'event_types_list' : [event_type],
                    'days'       : [dt]
                    },  **nav_bar())

    return render(request, template, context)

def today_event_type(
        request,
        event_type_id,
        template='catho/event_by_date.html'
    ):

    dt = datetime.today()
    return _single_day_event_type(request, event_type_id, dt, template)


def tomorrow_event_type(
        request,
        event_type_id,
        template='catho/event_by_date.html'
    ):

    dt = datetime.today()+timedelta(days=+1)
    return _single_day_event_type(request, event_type_id, dt, template)

def single_day_event_type(
        request,
        event_type_id,
        year,
        month,
        day,
        template='catho/event_by_date.html'
    ):

    dt = datetime(int(year), int(month), int(day))
    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    occurrences = Occurrence.objects.daily_occurrences(dt=dt).filter(event__event_type=event_type)

    context = dict({'occurrences': occurrences,
                    'event_types_list' : [event_type],
                    'days'       : [dt]
                    },  **nav_bar())

    return render(request, template, context)


def _add_event(
    request,
    template='catho/add_event.html',
    event_form_class=EventForm,
    recurrence_form_class=forms.SingleOccurrenceForm
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
            return http.HttpResponseRedirect(event.next_occurrence().get_absolute_url())

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class()
        #Caution: initial is a form_class parameter, not a request one.
        recurrence_form = recurrence_form_class(initial={'dtstart': dtstart})

    context = dict({'dtstart': dtstart, 'event_form': event_form, 'recurrence_form': recurrence_form}
                   , **nav_bar())

    return render(request, template, context)


def add_multiple_occurrence_event(request):
    return _add_event(request, recurrence_form_class=forms.MultipleOccurrenceForm)

def add_single_event(request):
    return _add_event(request)

def add_multiple_dates(
    request,
    template='catho/add_event_as_dates.html',
    event_form_class=EventForm,
    recurrence_form_class=SingleOccurrenceForm
    ):

    global supp_context
    dtstart = None
    OccurrenceFormSet = formset_factory(recurrence_form_class, extra=10)
    if request.method == 'POST':
        event_form = event_form_class(request.POST, request.FILES)
        formset = OccurrenceFormSet(request.POST)
        if event_form.is_valid() and formset.is_valid():
            event = event_form.save()
            for occurrence_form in formset:
                if occurrence_form.is_valid and occurrence_form.cleaned_data:
                    #if occurrence_form.cleaned_data['start_time'] is not None and occurrence_form.cleaned_data['end_time'] is not None:
                    print(occurrence_form.cleaned_data)
                    occurrence_form.save(event)
            return http.HttpResponseRedirect(event.next_occurrence().get_absolute_url())

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class()
        # initial parameter doesnt work here
        formset = OccurrenceFormSet()

    context = dict({'dtstart': dtstart,
                    'event_form': event_form,
                    'formset': formset,
                    }, **nav_bar())

    return render(request, template, context)


def new_event(request):
    return render(request, 'catho/add_event_choice.html', nav_bar())