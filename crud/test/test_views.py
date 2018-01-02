# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.http import HttpResponse
from django.shortcuts import render
from topic.models import Topic
from django.forms import formset_factory
from crud.forms import (EventTypeByTopicForm,
                        MultipleOccurrenceForm,
                        SingleOccurrenceForm,
                        FormsListManager,
                        EventForm,
                        )

from topic.models import EnjoyTodayUser, Event


# run by hand two_event_types_test url to run this test... nothing better for the moment


def two_event_types_test(request, template='test/two_event_types_forms_test.html'):

    manager = FormsListManager()
    only_one_form_error = False

    if request.method == 'POST':
        topic_forms = [EventTypeByTopicForm(topic, request.POST) for topic in Topic.objects.all()]

        manager.check_filled_forms(topic_forms)

        if manager.only_one_form_is_filled():
            manager.set_filled_form()
            filled_form = manager.filled_form
            msg1 = "only one form is valid"

            if filled_form.is_valid():
                event_type = filled_form.cleaned_data['event_type']
                msg2 = "filled_form is valid"

                return HttpResponse(msg1 + " AND " + msg2 + " AND " + "label : " + event_type.label)

        else:
            # flush all if more than one form has been filled
            topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]
            only_one_form_error = True

    else:
        topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]

    context = {'topic_forms': topic_forms,
               'error': only_one_form_error,
               }

    return render(request, template, context)


def occurrences_test(request, template='test/test_occurrences_forms.html'):

    manager = FormsListManager()
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm, extra=1, min_num=1, validate_min=True)

    if request.method == 'POST':
        dates_formset = SingleOccurrenceFormSet(request.POST)
        multiple_occurrence_form = MultipleOccurrenceForm(request.POST)

        manager.check_filled_forms([dates_formset, multiple_occurrence_form])

        if manager.only_one_form_is_filled():
            manager.set_filled_form()
            filled_form = manager.filled_form
            msg1 = "only one form has been filled"

            if filled_form.is_valid():
                # valid_form.save()
                msg2 = "the date is correct"
                return HttpResponse(msg1 + " AND " + msg2)

            else:
                return HttpResponse(msg1 + " but date not correct")

        else:
            # flush all if more than one form has been filled
            dates_formset = SingleOccurrenceFormSet()
            multiple_occurrence_form = MultipleOccurrenceForm()
            manager.error = True

    else:
        dates_formset = SingleOccurrenceFormSet()
        multiple_occurrence_form = MultipleOccurrenceForm()

    context = {'formset': dates_formset,
               'multiple_occurrence_form': multiple_occurrence_form,
               'error': manager.error,
               }

    return render(request, template, context)


def test_occurrences_as_formset(request, template='test/test_occurrences_as_formset.html'):

    manager = FormsListManager()
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm, min_num=1, validate_min=True)
    MultipleOccurrenceFormSet = formset_factory(MultipleOccurrenceForm, min_num=1, max_num=1, validate_min=True)

    if request.method == 'POST':
        dates_formset = SingleOccurrenceFormSet(request.POST)
        multiple_occurrence_formset = MultipleOccurrenceFormSet(request.POST)

        manager.check_filled_forms([dates_formset, multiple_occurrence_formset])

        if manager.only_one_form_is_filled():
            manager.set_filled_form()
            filled_form = manager.filled_form
            msg1 = "only one form has been filled"

            if filled_form.is_valid():
                # valid_form.save()
                msg2 = "the date is correct"
                return HttpResponse(msg1 + " AND " + msg2)

            else:
                return HttpResponse(msg1 + " but date not correct")

        else:
            # flush all if more than one form has been filled
            dates_formset = SingleOccurrenceFormSet()
            multiple_occurrence_formset = MultipleOccurrenceFormSet()
            manager.error = True

    else:
        dates_formset = SingleOccurrenceFormSet()
        multiple_occurrence_formset = MultipleOccurrenceFormSet()

    context = {'dates_formset': dates_formset,
               'multiple_occurrence_formset': multiple_occurrence_formset,
               'error': manager.error,
               }

    return render(request, template, context)


def add_event_test(request,
                   template='test/add_event_test.html'
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

    # intiating topics stuff
    topic_forms_manager = FormsListManager()

    # initiating event stuff
    event_planner = EnjoyTodayUser.objects.get(user=request.user)

    # initiating occurrences stuff
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm,
                                              min_num=1,
                                              validate_min=True)
    occurrences_forms_manager = FormsListManager()

    # -----------------------------------------------------------

    if request.method == 'POST':
        # initialization
        topic_forms = [EventTypeByTopicForm(topic, request.POST) for topic in Topic.objects.all()]
        event_form = EventForm(request.POST, request.FILES)
        single_occurrence_formset = SingleOccurrenceFormSet(request.POST)
        multiple_occurrence_form = MultipleOccurrenceForm(request.POST)

        # validation

        ## checking multiple forms
        topic_forms_manager.check_filled_forms(topic_forms)
        occurrences_forms_manager.check_filled_forms([single_occurrence_formset, multiple_occurrence_form])

        if topic_forms_manager.only_one_form_is_filled():
            topic_forms_manager.set_filled_form()

            if occurrences_forms_manager.only_one_form_is_filled():
                occurrences_forms_manager.set_filled_form()

                # validation of each form
                if occurrences_forms_manager.filled_form.is_valid() and \
                        topic_forms_manager.filled_form.is_valid() and \
                        event_form.is_valid():

                    # TODO: finish this
                    #return HttpResponse("Success")
                    # need to code something like this:
                    event_type = topic_forms_manager.filled_form.cleaned_data['event_type']
                    event = event_form.save(commit=False)
                    event.event_type = event_type
                    event.event_planner = event_planner
                    event.save()
                    # Todo: .save doesn't work here
                    occurrence = occurrences_forms_manager.filled_form.save(commit=False)
                    occurrence.event = event
                    occurrence.save()


            else:
                occurrences_forms_manager.error = True
                single_occurrence_formset = SingleOccurrenceFormSet()
                multiple_occurrence_form = MultipleOccurrenceForm()

        else:
            topic_forms_manager.error = True
            topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]

    else:
        topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]
        event_form = EventForm()
        single_occurrence_formset = SingleOccurrenceFormSet()
        multiple_occurrence_form = MultipleOccurrenceForm()

    context = {'topic_forms': topic_forms,
               'event_form': event_form,
               'single_occurrence_formset': single_occurrence_formset,
               'multiple_occurrence_form': multiple_occurrence_form,
               'topic_error': topic_forms_manager.error,
               'occurrence_error': occurrences_forms_manager.error,
               }

    return render(request, template, context)
