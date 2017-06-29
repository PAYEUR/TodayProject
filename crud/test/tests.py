from crud.forms import EventTypeByTopicForm, EventTypeByTopicFormsListManager
from django.http import HttpResponse
from django.shortcuts import render


def two_forms_test(request, template='crud/two_forms_test.html'):

    manager = EventTypeByTopicFormsListManager(request)
    valid_form = manager.valid_form

    # Macro validation: only one form must be valid
    if valid_form is not None:
        event_type = valid_form.cleaned_data['event_type']
        return HttpResponse("label : " + event_type.label)

    else:
        return render(request, template, manager.context)