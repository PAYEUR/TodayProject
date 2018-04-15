# coding = utf-8
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import formset_factory
from django.views.generic import UpdateView, DeleteView, ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from topic.models import Occurrence, Event, Topic, EventType
from connection.models import EnjoyTodayUser

from forms import (EventTypeByTopicForm,
                   MultipleOccurrenceForm,
                   SingleOccurrenceForm,
                   FormsListManager,
                   EventForm,
                   )


def has_event_planner(user, event):
        if event.event_planner:
            return user == event.event_planner.user
        else:
            return False


@login_required(login_url='connection:login')
def add_event_and_occurrences(request, template='crud/add_event_and_occurrences.html'):
    """
    # number of dates: number of extra dates forms to display
    Testing one single form to insert data in database. One single template and one single view.
    The form consists in 3 part:
    1) first block given by the topic and corresponding event_types
    2) second block given by commons event characteristics (image...)
    3) third block given by the kind of occurrences (single, multiples or dates).

    """

    # initiating event stuff
    event_planner = EnjoyTodayUser.objects.get(user=request.user)

    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm,
                                              min_num=1,
                                              extra=9,  # or number_of_extra_dates_forms
                                              validate_min=True)

    MultipleOccurrenceFormSet = formset_factory(MultipleOccurrenceForm,
                                                extra=0,
                                                min_num=1,
                                                validate_min=True,
                                                )

    occurrence_error = False
    topic_error = False

    # -----------------------------------------------------------

    if request.method == 'POST':
        # initialization
        event_form = EventForm(request.POST, request.FILES)

        single_occurrence_formset = SingleOccurrenceFormSet(request.POST, prefix='single_occurrence')
        multiple_occurrence_formset = MultipleOccurrenceFormSet(request.POST, prefix='multiple_occurrence')

        topic_forms = (EventTypeByTopicForm(request.POST, topic=topic) for topic in Topic.objects.all())
        topic_forms_manager = FormsListManager(*topic_forms)
        occurrences_forms_manager = FormsListManager(single_occurrence_formset, multiple_occurrence_formset)

        # reset forms if needed
        try:
            topic_forms_manager.filled_form.is_valid()
        except AttributeError:
            topic_error = True
            topic_forms = (EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all())
        else:
            try:
                occurrences_forms_manager.filled_form.is_valid()
            except AttributeError:
                occurrence_error = True
                single_occurrence_formset = SingleOccurrenceFormSet(prefix='single_occurrence')
                multiple_occurrence_formset = MultipleOccurrenceFormSet(prefix='multiple_occurrence')
            else:
                if occurrences_forms_manager.filled_form.is_valid() and \
                        topic_forms_manager.filled_form.is_valid() and \
                        event_form.is_valid():

                    # saving event
                    event = event_form.save(commit=False)
                    event.event_type = topic_forms_manager.filled_form.cleaned_data['event_type']
                    event.event_planner = event_planner
                    event.save()

                    # saving occurrence
                    # as occurrences_forms_manager.filled_form are formsets, one need a loop to call .save()
                    for form in occurrences_forms_manager.filled_form:
                        # has_changed doesn't take empty occurrences into account
                        # is_valid trigger clean method
                        if form.has_changed() and form.is_valid():
                            form.save(event)

                    return redirect('crud:event_planner_panel')

    else:
        topic_forms = (EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all())
        event_form = EventForm()
        single_occurrence_formset = SingleOccurrenceFormSet(prefix='single_occurrence')
        multiple_occurrence_formset = MultipleOccurrenceFormSet(prefix='multiple_occurrence')

    context = {'topic_forms': list(topic_forms),
               'event_form': event_form,
               'single_occurrence_formset': single_occurrence_formset,
               'multiple_occurrence_formset': multiple_occurrence_formset,
               'topic_error': topic_error,
               'occurrence_error': occurrence_error,
               }

    return render(request, template, context)


@login_required(login_url='connection:login')
def update_event(request, event_id, template='crud/update_event.html'):
    """
    """

    # initiating event stuff
    event_planner = EnjoyTodayUser.objects.get(user=request.user)
    topic_error = False
    current_event = get_object_or_404(Event, pk=event_id)
    try:
        current_topic = get_object_or_404(Topic, pk=current_event.event_type.topic.pk)
    except AttributeError:
        current_topic = Topic.objects.get(name='spi')

    # -----------------------------------------------------------

    if request.method == 'POST':
        # initialization
        event_form = EventForm(request.POST, request.FILES)
        topic_forms = [EventTypeByTopicForm(request.POST, topic=topic) for topic in Topic.objects.all()]

        topic_forms_manager = FormsListManager(*topic_forms)

        # reset forms if needed
        try:
            topic_forms_manager.filled_form.is_valid()
        except AttributeError:
            topic_error = True
            topic_forms = [EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all()]
        else:
            if topic_forms_manager.filled_form.is_valid() and event_form.is_valid():

                # saving event
                event = event_form.save(commit=False)
                event.event_type = topic_forms_manager.filled_form.cleaned_data['event_type']
                event.event_planner = event_planner
                event.save()

                return redirect('crud:event_planner_panel')

    else:
        event_form = EventForm(instance=current_event)

        topic_forms = []
        for topic in Topic.objects.all():
            if topic == current_topic:
                topic_forms.append(EventTypeByTopicForm(topic=topic,
                                                        initial={'event_type': current_event.event_type}))
            else:
                topic_forms.append(EventTypeByTopicForm(topic=topic))

    context = {'topic_forms': topic_forms,
               'event_form': event_form,
               'topic_error': topic_error,
               }

    return render(request, template, context)


class DeleteEvent(UserPassesTestMixin, DeleteView):

    # mixin parameters
    raise_exception = True

    model = Event
    template_name = 'crud/delete_event.html'
    success_url = reverse_lazy('crud:event_planner_panel')

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

    # mixin parameters
    raise_exception = True

    model = Occurrence
    template_name = 'crud/delete_occurrence.html'
    success_url = reverse_lazy('crud:event_planner_panel')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('occurrence_id')
        return get_object_or_404(Occurrence, pk=pk)

    # condition to be authorized to CRUD
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
    # form_class = SingleOccurrenceForm
    success_url = reverse_lazy('crud:event_planner_panel')
    raise_exception = True

    # condition to be authorized to CRUD
    def test_func(self):
        if self.get_object().event.event_planner:
            return self.request.user == self.get_object().event.event_planner.user
        else:
            return False

    def get_object(self, queryset=None):
        pk = self.kwargs.get('occurrence_id')
        return get_object_or_404(Occurrence, pk=pk)


# ------------------------------------------------------------------------------------------
class EventPlannerPanelView(LoginRequiredMixin, ListView):

    # mixin parameters
    login_url = 'connection:login'

    # view parameters
    model = Event
    context_object_name = 'events'
    template_name = 'crud/event_planner_panel.html'

    def get_event_planner(self):
        return EnjoyTodayUser.objects.get(user=self.request.user)

    def get_queryset(self):
        return Event.objects.filter(event_planner=self.get_event_planner()).order_by('location')

    def get_context_data(self, **kwargs):
        context = super(EventPlannerPanelView, self).get_context_data(**kwargs)
        context['event_planner'] = self.get_event_planner()

        return context