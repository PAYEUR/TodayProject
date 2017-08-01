# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from crud.forms import FormsListManager
from django.http import HttpResponse
from django.shortcuts import render
from topic.models import Topic
from crud.forms import EventTypeByTopicForm, MultipleOccurrenceForm, SingleOccurrenceForm
from django.forms import formset_factory


# run by hand two_forms_test url to run this test... nothing better for the moment


def two_event_types_test(request, template='test/two_event_types_forms_test.html'):

    manager = FormsListManager()
    only_one_form_error = False

    if request.method == 'POST':
        topic_forms = [EventTypeByTopicForm(topic, request.POST) for topic in Topic.objects.all()]

        manager.check_filled_forms(topic_forms)

        if manager.only_one_form_is_filled():
            manager.set_filled_form()
            filled_form = manager.filled_form

            if filled_form.is_valid():
                event_type = filled_form.cleaned_data['event_type']
                return HttpResponse("label : " + event_type.label)

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


def occurrences_test(request, template='test/two_occurrences_forms_test.html'):

    manager = FormsListManager()
    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm, extra=1, min_num=1, validate_min=True)

    if request.method == 'POST':
        dates_formset = SingleOccurrenceFormSet(request.POST)
        multiple_occurrence_form = MultipleOccurrenceForm(request.POST)

        manager.check_filled_forms([dates_formset, multiple_occurrence_form])

        if manager.only_one_form_is_filled():
            manager.set_filled_form()
            filled_form = manager.filled_form

            if filled_form.is_valid():
                # valid_form.save()
                return HttpResponse("Un seul formulaire a été rempli")

            # else print errors

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
