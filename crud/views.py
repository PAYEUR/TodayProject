from django.shortcuts import get_object_or_404, render, redirect
from django.forms import formset_factory
from django.views.generic import UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import (EventTypeByTopicForm,
                    MultipleOccurrenceForm,
                    SingleOccurrenceForm,
                    FormsListManager,
                    EventForm,
                    )


from topic.models import Occurrence, Event, EnjoyTodayUser, Topic


# new views

@login_required(login_url='connection:login')
def add_event(request,
              # number_of_extra_dates_forms,
              template='crud/add_event.html'
              ):
    """
    # number of dates: number of extra dates forms to display
    Testing one single form to insert data in database. One single template and one single view.
    The form consists in 3 part:
    1) first block given by the topic and corresponding event_types
    2) second block given by commons event characteristics (image...)
    3) third block given by the kind of occurrences (single, multiples or dates).

    """

    # intiating topics stuff
    topic_forms_manager = FormsListManager()

    # initiating event stuff
    event_planner = EnjoyTodayUser.objects.get(user=request.user)

    # initiating occurrences stuff
    occurrences_forms_manager = FormsListManager()
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm,
                                              min_num=1,
                                              extra=9,  # or number_of_extra_dates_forms
                                              validate_min=True)

    MultipleOccurrenceFormSet = formset_factory(MultipleOccurrenceForm,
                                                extra=0,
                                                min_num=1,
                                                max_num=1,
                                                validate_min=True,
                                                validate_max=True)

    # -----------------------------------------------------------

    if request.method == 'POST':
        # initialization
        topic_forms = [EventTypeByTopicForm(topic, request.POST) for topic in Topic.objects.all()]
        event_form = EventForm(request.POST, request.FILES)
        single_occurrence_formset = SingleOccurrenceFormSet(request.POST, prefix="single")
        multiple_occurrence_formset = MultipleOccurrenceFormSet(request.POST, prefix="multiple")

        # validation

        # checking multiple forms
        topic_forms_manager.check_filled_forms(topic_forms)
        occurrences_forms_manager.check_filled_forms([single_occurrence_formset, multiple_occurrence_formset])

        if topic_forms_manager.only_one_form_is_filled():
            topic_forms_manager.set_filled_form()

            if occurrences_forms_manager.only_one_form_is_filled():
                occurrences_forms_manager.set_filled_form()
                occurrences_formset = occurrences_forms_manager.filled_form

                # validation of each form
                if occurrences_formset.is_valid() and \
                   topic_forms_manager.filled_form.is_valid() and \
                   event_form.is_valid():

                    # reset potential error messages
                    occurrences_forms_manager.error = False
                    topic_forms_manager.error = False

                    # saving event
                    event = event_form.save(commit=False)
                    event.event_type = topic_forms_manager.filled_form.cleaned_data['event_type']
                    event.event_planner = event_planner
                    event.save()

                    # saving occurrence
                    # as occurrences_forms_manager.filled_form are formsets, one need a loop to call .save()
                    for form in occurrences_formset:
                        print(occurrences_formset)
                        if form.is_valid and form.cleaned_data:  # TODO: check the syntax and utility of this assertion
                            print(form.cleaned_data)
                            print("event_saved")

                    return redirect('core:event_planner_panel')

            else:
                occurrences_forms_manager.error = True
                single_occurrence_formset = SingleOccurrenceFormSet(prefix="single")
                multiple_occurrence_formset = MultipleOccurrenceFormSet(prefix="multiple")

        else:
            topic_forms_manager.error = True
            # reset forms
            topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]

    else:
        topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]
        event_form = EventForm()
        single_occurrence_formset = SingleOccurrenceFormSet(prefix="single")
        multiple_occurrence_formset = MultipleOccurrenceFormSet(prefix="multiple")

    context = {'topic_forms': topic_forms,
               'event_form': event_form,
               'single_occurrence_formset': single_occurrence_formset,
               'multiple_occurrence_formset': multiple_occurrence_formset,
               'topic_error': topic_forms_manager.error,
               'occurrence_error': occurrences_forms_manager.error,
               }

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

    # mixin parameters
    raise_exception = True

    model = Occurrence
    template_name = 'crud/delete_occurrence.html'
    success_url = reverse_lazy('core:event_planner_panel')

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
    success_url = reverse_lazy('core:event_planner_panel')
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


def test_func(user, event):
        if event.event_planner:
            return user == event.event_planner.user
        else:
            return False


# Todo: create AddOccurrences(view)