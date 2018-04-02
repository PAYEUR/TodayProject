# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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

    only_one_form_error = False

    if request.method == 'POST':
        print('post request')
        topic_forms = (EventTypeByTopicForm(request.POST, topic=topic) for topic in Topic.objects.all())

        manager = FormsListManager(*topic_forms)

        if not manager.filled_form:
            print("not only one form is valid")
            only_one_form_error = True
            topic_forms = (EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all())

        elif manager.filled_form.is_valid():
            print("first if triggered")
            event_type = manager.filled_form.cleaned_data['event_type']
            msg2 = "filled_form is valid"
            return HttpResponse(msg2 + " AND " + "label : " + event_type.label)

    else:
        topic_forms = (EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all())

    context = {'topic_forms': list(topic_forms),
               'error': only_one_form_error,
               }

    return render(request, template, context)


@login_required(login_url='connection:login')
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
    occurrences_forms_manager = FormsListManager()
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm,
                                              min_num=1,
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

                    return redirect('crud:event_planner_panel')

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


@login_required(login_url='connection:login')
def add_event_test2(request,
              # number_of_extra_dates_forms,
              template='test/add_event_test.html'
              ):
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
                                                #max_num=1,
                                                validate_min=True,
                                                #validate_max=True
                                                )

    occurrence_error = False
    topic_error = False

    # -----------------------------------------------------------
    if request.method == 'POST':
        print("post request")
        # initialization
        event_form = EventForm(request.POST, request.FILES)

        single_occurrence_formset = SingleOccurrenceFormSet(request.POST, prefix='single_occurrence')
        multiple_occurrence_formset = MultipleOccurrenceFormSet(request.POST, prefix='multiple_occurrence')

        topic_forms = (EventTypeByTopicForm(request.POST, topic=topic) for topic in Topic.objects.all())
        topic_forms_manager = FormsListManager(*topic_forms)
        occurrences_forms_manager = FormsListManager(single_occurrence_formset, multiple_occurrence_formset)

        # reset forms if needed
        if not topic_forms_manager.filled_form:
            topic_error = True
            topic_forms = (EventTypeByTopicForm(topic=topic) for topic in Topic.objects.all())

        if not occurrences_forms_manager.filled_form:
            occurrence_error = True
            single_occurrence_formset = SingleOccurrenceFormSet(prefix='single_occurrence')
            multiple_occurrence_formset = MultipleOccurrenceFormSet(prefix='multiple_occurrence')

        # validation
        elif occurrences_forms_manager.filled_form.is_valid() and \
                topic_forms_manager.filled_form.is_valid() and \
                event_form.is_valid():

            # saving event
            event = event_form.save(commit=False)
            event.event_type = topic_forms_manager.filled_form.cleaned_data['event_type']
            event.event_planner = event_planner
            event.save()

            # saving occurrence
            # as occurrences_forms_manager.filled_form are formsets, one need a loop to call .save()
            print(len(occurrences_forms_manager.filled_form))
            for form in occurrences_forms_manager.filled_form:
                print("I see a form")
                if form.has_changed() and form.is_valid():  # to trigger the clean method
                    form.save(event)
                    print(form.cleaned_data)
                    print("event_saved")

            return redirect('crud:event_planner_panel')


    else:
        print("non post request")
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
