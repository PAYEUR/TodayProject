import logging
from datetime import datetime

from django import http
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
from dateutil import parser
from django.forms import formset_factory
from django.views.generic import UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .forms import EventForm, SingleOccurrenceForm, MultipleOccurrenceForm, MultipleDateSingleOccurrenceForm
from topic.models import EventType, Occurrence, Event, EnjoyTodayUser
from core.utils import get_current_topic
from django.contrib.sites.shortcuts import get_current_site
from django.forms.models import model_to_dict



@login_required(login_url='connection:login')
def _add_event(
        request,
        recurrence_form_class,
        template='crud/add_event.html',
        event_form_class=EventForm,
        ):

        topic = get_current_topic(request)
        return _add_event_by_topic(request,
                                   topic,
                                   recurrence_form_class,
                                   template,
                                   event_form_class)


@login_required(login_url='connection:login')
def _add_event_by_topic(
        request,
        topic,
        recurrence_form_class,
        template='crud/add_event.html',
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
        event = Event(event_planner=EnjoyTodayUser.objects.get(user=request.user),
                      #site=get_current_site(request)
                      )

        event_form = event_form_class(topic, request.POST, request.FILES, instance=event)
        recurrence_form = recurrence_form_class(request.POST)
        if event_form.is_valid() and recurrence_form.is_valid():
            event.save()
            recurrence_form.save(event)
            return redirect('core:event_planner_panel')

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class(topic)
        # Caution: initial is a form_class parameter and not a request parameter.
        recurrence_form = recurrence_form_class(initial={'dtstart': dtstart})

    context = dict({'dtstart': dtstart,
                    'event_form': event_form,
                    'recurrence_form': recurrence_form,
                    },
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
        template='crud/add_event_as_dates.html',
        event_form_class=EventForm,
        ):

    dtstart = None
    topic = get_current_topic(request)

    OccurrenceFormSet = formset_factory(MultipleDateSingleOccurrenceForm, extra=10)
    if request.method == 'POST':
        # to add event_planner to event
        event = Event(event_planner=EnjoyTodayUser.objects.get(user=request.user),
                      #site=get_current_site(request)
                      )

        event_form = event_form_class(topic, request.POST, request.FILES, instance=event)
        formset = OccurrenceFormSet(request.POST)
        if event_form.is_valid() and formset.is_valid():
            event.save()
            for occurrence_form in formset:
                if occurrence_form.is_valid and occurrence_form.cleaned_data:
                    occurrence_form.save(event)
            return redirect('core:event_planner_panel')

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except(TypeError, ValueError) as exc:
                # TODO: A badly formatted date is passed to add_event
                logging.warning(exc)

        dtstart = dtstart or datetime.now()
        event_form = event_form_class(topic)
        # initial parameter doesnt work here
        formset = OccurrenceFormSet()

    context = dict({'dtstart': dtstart,
                    'event_form': event_form,
                    'formset': formset,
                    })

    return render(request, template, context)


class UpdateEvent(UserPassesTestMixin, UpdateView):

    model = Event
    template_name = 'crud/update_event.html'
    form_class = EventForm
    success_url = reverse_lazy('core:event_planner_panel')

    # mixin parameters
    raise_exception = True

    def get_form(self, form_class=form_class):
        return form_class(topic=get_current_topic(self.request), **self.get_form_kwargs())

    def get_object(self, queryset=None):
        pk = self.kwargs.get('event_id')
        return get_object_or_404(Event, pk=pk)

    # condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event_planner:
            return self.request.user == self.get_object().event_planner.user
        else:
            return False


class DeleteEvent(UserPassesTestMixin, DeleteView):

    # mixin parameters
    raise_exception = True

    model = Event
    template_name = 'crud/delete_event.html'
    success_url = reverse_lazy('core:event_planner_panel')


    def get_object(self, queryset=None):
        pk = self.kwargs.get('event_id')
        return get_object_or_404(Event, pk=pk)

    # condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event_planner:
            return self.request.user == self.get_object().event_planner.user
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(DeleteEvent, self).get_context_data(**kwargs)


class DeleteOccurrence(UserPassesTestMixin, DeleteView):

    #mixin parameters
    raise_exception = True

    model = Occurrence
    template_name = 'crud/delete_occurrence.html'
    success_url = reverse_lazy('core:event_planner_panel')


    def get_object(self, queryset=None):
        pk = self.kwargs.get('occurrence_id')
        return get_object_or_404(Occurrence, pk=pk)

    #condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event.event_planner:
            return self.request.user == self.get_object().event.event_planner.user
        else:
            return False


class UpdateOccurrence(UserPassesTestMixin, UpdateView):
    """ not possible to use form_class = SingleOccurrenceForm, as SingleOccurrenceForm is not a ModelForm
    """

    template_name = 'crud/update_occurrence.html'
    fields = ['start_time', 'end_time']
    #form_class = SingleOccurrenceForm
    success_url = reverse_lazy('core:event_planner_panel')
    raise_exception = True

    #condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event.event_planner:
            return self.request.user == self.get_object().event.event_planner.user
        else:
            return False

    def get_object(self, queryset=None):
        pk = self.kwargs.get('occurrence_id')
        return get_object_or_404(Occurrence, pk=pk)


def test_func(user, Event):
        if Event.event_planner:
            return user == Event.event_planner.user
        else:
            return False

# TODO: check how to include this in the occurrence manager
@login_required(login_url='connection:login')
def add_multiples_occurrences(
        request,
        event_id,
        template='crud/add_multiple_occurrences.html',
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
    OccurrenceFormSet = formset_factory(MultipleDateSingleOccurrenceForm, extra=10)
    #passes_test
    if test_func(request.user, event):
        if request.method == 'POST':
            formset = OccurrenceFormSet(request.POST)
            if formset.is_valid():
                for occurrence_form in formset:
                    if occurrence_form.is_valid and occurrence_form.cleaned_data:
                        occurrence_form.save(event)
                return http.HttpResponseRedirect(reverse_lazy('core:event_planner_panel'))

        else:
            dtstart = datetime.now()
            # initial parameter doesnt work here
            formset = OccurrenceFormSet()


        context = dict({'dtstart': dtstart,
                        'formset': formset,
                        'event': event,
                        }
                       )

        return render(request, template, context)

    else:
        raise PermissionDenied


@login_required(login_url='connection:login')
def new_event(request):
    context = dict()
    return render(request, 'crud/add_event_choice.html', context)