import calendar
import logging


from datetime import datetime, timedelta
from django import http
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect

from dateutil import parser

from .forms import EventForm, IndexForm, SingleOccurrenceForm, MultipleOccurrenceForm
from django.forms import formset_factory
from .models import EventType, Occurrence, Event, EventPlanner
from django.views.generic import UpdateView, ListView, DeleteView #, CreateView
from django.core.urlresolvers import reverse_lazy


from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


from . import swingtime_settings

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


#TODO: surcharg base template to add nav_list to each context
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
            # dont use city from now
            event_type = form.cleaned_data['quoi']
            date = form.cleaned_data['quand']

            if event_type is not None:
                return redirect('catho:single_day_event_type',
                                event_type_id=event_type.pk,
                                year=date.year,
                                month=date.month,
                                day=date.day)
            else:
                return redirect('catho:daily_events',
                                year=date.year,
                                month=date.month,
                                day=date.day)
    else:
        form = IndexForm()

    context = dict({'form': form,
                    }, **nav_bar()
                   )

    return render(request, template, context)


# TODO use genericview instead of get_occurrence function
def get_occurrence(request, occurrence_id):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)
    # TODO overwrite context to add address
    if occurrence.event.address != "non precise":
        address = occurrence.event.address + ", France"
    else:
        address = False

    context = dict({'occurrence': occurrence,
                    'address': address,
                    }, **nav_bar()
                   )
    return render(request, 'catho/single_event.html', context)


def _events_in_a_period(request, days, template='catho/event_by_date.html'):
    """

    :param request:
    :param days: a list of days
    :return: context with occurrences, event_types_list and days
    """
    # not satisfying because len(moment) times database requests

    # print event_types occurrences
    # TODO: verify the following point: enormous bugg: if no event at all in coming days => crash?!
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day)#.filter(is_multiple=False)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    # get all related event_types  (double sorted)
    events_list = [occurrence.event for occurrence in occurrences]
    event_types_list = list(set([event.event_type for event in events_list]))

    context = dict({'occurrences': occurrences,
                   'event_types_list': event_types_list,
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
    days = [datetime.today() + timedelta(days=+1)]
    return _events_in_a_period(request, days, template)


def coming_days_events(request, next_days_duration=3, template='catho/event_by_date.html'):
    """

    :param request:
    :param next_days_duration: how many days does "coming_days" mean
    :param template:
    :return: all events for coming_days
    """
    today = datetime.now()
    i = 0
    days = []
    while i < int(next_days_duration):
        days.append(today + timedelta(days=+i))
        i += 1

    return _events_in_a_period(request, days, template)


def daily_events(request, year, month, day, template='catho/event_by_date.html'):

    days = [datetime(int(year), int(month), int(day))]

    return _events_in_a_period(request, days, template)


def monthly_events(request, year, month, template='catho/event_by_date.html'):

    year, month = int(year), int(month)
    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(year, month)
    days = []
    for week in weeks:
        for day in week:
            days.append(day)

    return _events_in_a_period(request, days, template)


def event_type_coming_days(request, event_type_id, next_days_duration=3, template='catho/date_by_event_type.html'):
    """

    :param request:
    :param event_type_id:
    :param next_days_duration:
    :param template:
    :return: every occurrences of a single event_type within next_day_duration days
    """

    # list of next_day_duration days
    today = datetime.now()
    i = 0
    days = []
    while i < int(next_days_duration):
        days.append(today + timedelta(days=+i))
        i += 1

    # sort event_type.occurrences by day
    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day).filter(event__event_type=event_type)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    context = dict({'occurrences': occurrences,
                    'event_type': event_type,
                    },  **nav_bar()
                   )

    return render(request, template, context)


def _single_day_event_type(
        request,
        event_type_id,
        dt,
        template='catho/event_by_date.html'
        ):

    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    occurrences = Occurrence.objects.daily_occurrences(dt=dt).filter(event__event_type=event_type)

    context = dict({'occurrences': occurrences,
                    'event_types_list': [event_type],
                    'days': [dt]
                    },  **nav_bar()
                   )

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
                    'event_types_list': [event_type],
                    'days': [dt]
                    },  **nav_bar()
                   )

    return render(request, template, context)


@login_required(login_url='connection:login')
def _add_event(
        request,
        recurrence_form_class,
        template='catho/add_event.html',
        event_form_class=EventForm,
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
        :rtype: object

    """

    dtstart = None
    if request.method == 'POST':
        # to add event_planner to event
        event = Event(event_planner = EventPlanner.objects.get(user=request.user))
        event_form = event_form_class(request.POST, request.FILES, instance=event)
        recurrence_form = recurrence_form_class(request.POST)
        if event_form.is_valid() and recurrence_form.is_valid():
            event.save()
            recurrence_form.save(event)
            return redirect('catho:event_planner_panel')

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class()
        # Caution: initial is a form_class parameter and not a request parameter.
        recurrence_form = recurrence_form_class(initial={'dtstart': dtstart})

    context = dict({'dtstart': dtstart, 'event_form': event_form, 'recurrence_form': recurrence_form},
                   **nav_bar()
                   )

    return render(request, template, context)


@login_required(login_url='connection:login')
def add_multiple_occurrence_event(request, recurrence_form_class=MultipleOccurrenceForm):
    return _add_event(request, recurrence_form_class)


@login_required(login_url='connection:login')
def add_single_event(request, recurrence_form_class=SingleOccurrenceForm):
    return _add_event(request, recurrence_form_class)


@login_required(login_url='connection:login')
def add_multiple_dates(
        request,
        template='catho/add_event_as_dates.html',
        event_form_class=EventForm,
        ):

    dtstart = None
    OccurrenceFormSet = formset_factory(SingleOccurrenceForm, extra=10)
    if request.method == 'POST':
        # to add event_planner to event
        event = Event(event_planner = EventPlanner.objects.get(user=request.user))
        event_form = event_form_class(request.POST, request.FILES, instance=event)
        formset = OccurrenceFormSet(request.POST)
        if event_form.is_valid() and formset.is_valid():
            event.save()
            for occurrence_form in formset:
                if occurrence_form.is_valid and occurrence_form.cleaned_data:
                    occurrence_form.save(event)
            return redirect('catho:event_planner_panel')

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
                    }, **nav_bar()
                   )

    return render(request, template, context)


@login_required(login_url='connection:login')
def new_event(request):
    return render(request, 'catho/add_event_choice.html', nav_bar())


class EventPlannerPanel(LoginRequiredMixin, ListView):

    #mixin parameters
    login_url = 'connection:login'

    ## view parameters
    model = Event
    context_object_name = "events"
    template_name = "catho/event_planner_panel.html"
    ## context and query parameters
    # event_planner = recupere depuis les infos de session normalement
    #event_planner = EventPlanner.objects.get(user__username="payeur")

    def get_event_planner(self):
        return EventPlanner.objects.get(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(event_planner=self.get_event_planner())

    def get_context_data(self, **kwargs):
        context = super(EventPlannerPanel, self).get_context_data(**kwargs)
        context['event_planner'] = self.get_event_planner()
        # instead of navbar()
        context['nav_list'] = get_list_or_404(EventType)

        return context


class UpdateEvent(UserPassesTestMixin, UpdateView):

    model = Event
    template_name = 'catho/update_event.html'
    form_class = EventForm
    success_url = reverse_lazy('catho:event_planner_panel')
    #success_url = event_planner.get_absolute_url()

    #mixin parameters
    raise_exception = True

    def get_object(self, queryset=None):
        pk = self.kwargs.get('event_id')
        return get_object_or_404(Event, pk=pk)

    #condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event_planner:
            return self.request.user == self.get_object().event_planner.user
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(UpdateEvent, self).get_context_data(**kwargs)
        # instead of navbar()
        context['nav_list'] = get_list_or_404(EventType)

        return context



class DeleteEvent(UserPassesTestMixin, DeleteView):

    #mixin parameters
    raise_exception = True

    model = Event
    template_name = "catho/delete_event.html"
    success_url = reverse_lazy('catho:event_planner_panel')


    def get_object(self, queryset=None):
        pk = self.kwargs.get('event_id')
        return get_object_or_404(Event, pk=pk)

    #condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event_planner:
            return self.request.user == self.get_object().event_planner.user
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(DeleteEvent, self).get_context_data(**kwargs)
        # instead of navbar()
        context['nav_list'] = get_list_or_404(EventType)

        return context



class DeleteOccurrence(UserPassesTestMixin, DeleteView):

    #mixin parameters
    raise_exception = True

    model = Occurrence
    template_name = "catho/delete_occurrence.html"
    success_url = reverse_lazy('catho:event_planner_panel')



    def get_object(self, queryset=None):
        pk = self.kwargs.get('occurrence_id')
        return get_object_or_404(Occurrence, pk=pk)

    #condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event.event_planner:
            return self.request.user == self.get_object().event.event_planner.user
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(DeleteOccurrence, self).get_context_data(**kwargs)
        # instead of navbar()
        context['nav_list'] = get_list_or_404(EventType)

        return context


def test_func(user, Event):
        if Event.event_planner:
            return user == Event.event_planner.user
        else:
            return False


@login_required(login_url='connection:login')
def add_multiples_occurrences(
        request,
        event_id,
        template='catho/add_multiple_occurrences.html',
        recurrence_form_class=SingleOccurrenceForm
        ):
    """
    :param request:
    :param event_id:
    :param template:
    :param recurrence_form_class:
    :return: allow modifying existing event to add more occurrences
    """

    dtstart = None
    event = get_object_or_404(Event, pk=int(event_id))
    OccurrenceFormSet = formset_factory(recurrence_form_class, extra=10)
    #passes_test
    if test_func(request.user, event):
        if request.method == 'POST':
            formset = OccurrenceFormSet(request.POST)
            if formset.is_valid():
                for occurrence_form in formset:
                    if occurrence_form.is_valid and occurrence_form.cleaned_data:
                        occurrence_form.save(event)
                return http.HttpResponseRedirect(reverse_lazy('catho:event_planner_panel'))

        else:
            dtstart = datetime.now()
            # initial parameter doesnt work here
            formset = OccurrenceFormSet()


        context = dict({'dtstart': dtstart,
                        'formset': formset,
                        'event': event,
                        }, **nav_bar()
                       )

        return render(request, template, context)

    else:
        raise PermissionDenied

