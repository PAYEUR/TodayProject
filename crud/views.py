import logging
from datetime import datetime

from django import http
from django.shortcuts import get_object_or_404, render, redirect
from dateutil import parser
from django.forms import formset_factory
from django.views.generic import UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .forms import (EventForm,
                    SingleOccurrenceForm,
                    MultipleOccurrenceForm,
                    MultipleDateSingleOccurrenceForm,
                    EventTypeByTopicForm,
                    EventTypeByTopicFormsListManager,
                    )


from topic.models import Occurrence, Event, EnjoyTodayUser, Topic


# new views
def add_event2(request,
               template='crud/add_event2.html'
               ):
    """
    Testing one single form to insert data in database. One single template and one single view.
    The form consists in 3 part:
    1) first block given by the topic and corresponding event_types
    2) second block given by commons event characteristics (image...)
    3) third block given by the kind of occurrences (single, multiples or dates).

    # TODO: OccurrenceFormSet does not display as common form in the template, so has to be taken into consideration
    # TODO: validation
    """

    # OccurrenceFormSet = formset_factory(MultipleDateSingleOccurrenceForm, extra=10)
    event = Event(event_planner=EnjoyTodayUser.objects.get(user=request.user))

    if request.method == 'POST':
        # initialization
        topic_forms = [EventTypeForm(topic, request.POST) for topic in Topic.objects.all()]

        occurrence_forms = [SingleOccurrenceForm(request.POST),
                            MultipleOccurrenceForm(request.POST),
                            # MultipleDates
                            ]
        event_form = EventForm(request.POST, request.FILES, instance=event)

        # validation
        # TODO: to be tested
        valid_topic_forms = get_valid_forms(topic_forms)
        valid_occurrence_forms = get_valid_forms(occurrence_forms)

        if len(valid_topic_forms) == 1 and len(valid_occurrence_forms) == 1 and event_form.is_valid():

            topic_form = valid_topic_forms[0]
            occurrence_form = valid_occurrence_forms[0]

            event = event_form.save(commit=False)
            event.event_type = topic_form.cleaned_data['label']
            event.save()
            occurrence_form.save()
            return redirect('core:event_planner_panel')

    else:
        event_form = EventForm()
        topic_forms = [EventTypeForm(topic) for topic in Topic.objects.all()]
        occurrence_forms = [SingleOccurrenceForm(),
                            MultipleOccurrenceForm(),
                            # OccurrenceFormSet()
                            ]

    context = {'topic_forms': topic_forms,
               'occurrence_forms': occurrence_forms,
               'event_form': event_form,
               'media': occurrence_forms[0].media
               }

    return render(request, template, context)












# end of new views










# TODO: rewrite these vebose views. Only one view to post any kind of occurrences
@login_required(login_url='connection:login')
def _add_event(
        request,
        recurrence_form_class,
        template='crud/add_event.html',
        event_form_class=EventForm,
        ):

        # TODO: topic should become a form field
        topic = get_object_or_404(Topic, name='spi')
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

    # TODO: topic should become a form field
    topic = get_object_or_404(Topic, name='spi')

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
        return form_class(topic=Event.event_type.topic, **self.get_form_kwargs())

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
