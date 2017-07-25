# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from crud.forms import EventTypeByTopicFormsListManager, OccurrenceFormsListManager
from django.http import HttpResponse
from django.shortcuts import render


# run by hand two_forms_test url to run this test... nothing better for the moment
def two_event_types_test(request, template='test/two_event_types_forms_test.html'):

    manager = EventTypeByTopicFormsListManager(request)
    valid_form = manager.valid_form

    # Macro validation: only one form must be valid
    if valid_form is not None:
        event_type = valid_form.cleaned_data['event_type']
        return HttpResponse("label : " + event_type.label)

    else:
        return render(request, template, manager.context)


def occurrences_test(request, template='test/two_occurrences_forms_test.html'):

    manager = OccurrenceFormsListManager(request)
    valid_form = manager.valid_form

    if valid_form is not None:
        return HttpResponse("Un seul formulaire a été rempli")

    else:
        return render(request, template, manager.context)

