# coding=utf-8

from __future__ import print_function, unicode_literals

from datetime import datetime, date, time

from datetimewidget.widgets import TimeWidget
from django import forms
from django.utils.translation import ugettext_lazy as _

from core import swingtime_settings
from .models import EventType  #,City, Occurrence

WEEKDAY_LONG = (
    (0, _('Monday')),
    (1, _('Tuesday')),
    (2, _('Wednesday')),
    (3, _('Thursday')),
    (4, _('Friday')),
    (5, _('Saturday')),
    (6, _('Sunday')),
)


MINUTES_INTERVAL = swingtime_settings.TIMESLOT_INTERVAL.seconds // 60


# IndexForm

class IndexForm(forms.Form):
    """
    Get the 3 main informations to print on the index page
    The field "quoi" corresponding to EventTypes is dynamically dispatched
    """

    def __init__(self, topic, *args, **kwargs):
        super(IndexForm, self).__init__(*args, **kwargs)
        self.topic = topic

        self.fields['quoi'] = forms.ModelMultipleChoiceField(
            EventType.objects.filter(topic=topic),
            label='Quoi ?',
            required=False,
            #empty_label=None,
            widget=forms.widgets.CheckboxSelectMultiple)


    quand = forms.DateField(
            label='Quand ?',
            required=True,
            #initial=datetime.today,
            #widget=DateWidget(
                #options={
                    #'todayHighlight': True,
                    #'weekStart': 1,
                    #'pickerPosition': 'top-left'
                #},
                #usel10n=True,
                #bootstrap_version=3)
            widget=forms.widgets.HiddenInput
            )

    start_hour = forms.TimeField(
                label="Début",
                required="False",
                initial=time.min,
                widget=TimeWidget(
                    options={
                        'pickerPosition': 'top-left',
                        'minuteStep': 15,
                    },
                    usel10n=False,
                    bootstrap_version=3)
                )

    end_hour = forms.TimeField(
                label="Fin",
                required="False",
                initial=time.max,
                widget=TimeWidget(
                    options={
                        'pickerPosition': 'top-left',
                        'minuteStep': 15,
                    },
                    usel10n=False,
                    bootstrap_version=3)
                )

    # ---------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(IndexForm, self).clean()
        quand = cleaned_data['quand']
        starting_hour = cleaned_data['start_hour']
        ending_hour = cleaned_data['end_hour']

        if starting_hour and ending_hour:
            if starting_hour > ending_hour:
                raise forms.ValidationError("Verifier que les heures correspondent")

        if quand < date.today():
            raise forms.ValidationError("Verifier que les dates correspondent")

        return self.cleaned_data

# -------------------------------------------------------------------------------
def timeslot_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT
):
    """
    Create a list of time slot options for use in swingtime forms.

    The list is comprised of 2-tuples containing a 24-hour time value and a
    12-hour temporal representation of that offset.

    """
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    while dtstart <= dtend:
        options.append((str(dtstart.time()), dtstart.strftime(fmt)))
        dtstart += interval

    return options