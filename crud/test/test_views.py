from crud.forms import EventTypeByTopicFormsListManager, OccurrenceFormsListManager
from django.http import HttpResponse
from django.shortcuts import render


# run by hand two_forms_test url to run this test... nothing better for the moment
def two_forms_test(request, template='test/two_event_types_forms_test.html'):

    manager = EventTypeByTopicFormsListManager(request)
    valid_form = manager.valid_form

    # Macro validation: only one form must be valid
    if valid_form is not None:
        event_type = valid_form.cleaned_data['event_type']
        return HttpResponse("label : " + event_type.label)

    else:
        return render(request, template, manager.context)


def two_forms_test2(request, template='test/two_occurrences_forms_test.html'):

    manager = OccurrenceFormsListManager(request)
    valid_form = manager.valid_form

    # TODO: finish this