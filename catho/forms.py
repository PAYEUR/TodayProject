"""
Convenience forms for adding and updating ``Event`` and ``Occurrence``s.

"""
from __future__ import print_function, unicode_literals
from datetime import datetime, date, time, timedelta
from django import VERSION
from django import forms
from django.forms.widgets import TimeInput
from django.forms.extras.widgets import SelectDateWidget
from datetimewidget.widgets import DateWidget, DateTimeWidget, TimeWidget
from django.utils.translation import ugettext_lazy as _

from dateutil import rrule
from . import swingtime_settings
from .models import Event, EventType #,City, Occurrence
from . import utils

FIELDS_REQUIRED = (VERSION[:2] >= (1, 6))

WEEKDAY_SHORT = (
    (7, _('Sun')),
    (1, _('Mon')),
    (2, _('Tue')),
    (3, _('Wed')),
    (4, _('Thu')),
    (5, _('Fri')),
    (6, _('Sat'))
)

WEEKDAY_LONG = (
    (7, _('Sunday')),
    (1, _('Monday')),
    (2, _('Tuesday')),
    (3, _('Wednesday')),
    (4, _('Thursday')),
    (5, _('Friday')),
    (6, _('Saturday'))
)

MONTH_LONG = (
    (1,  _('January')),
    (2,  _('February')),
    (3,  _('March')),
    (4,  _('April')),
    (5,  _('May')),
    (6,  _('June')),
    (7,  _('July')),
    (8,  _('August')),
    (9,  _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December')),
)

MONTH_SHORT = (
    (1,  _('Jan')),
    (2,  _('Feb')),
    (3,  _('Mar')),
    (4,  _('Apr')),
    (5,  _('May')),
    (6,  _('Jun')),
    (7,  _('Jul')),
    (8,  _('Aug')),
    (9,  _('Sep')),
    (10, _('Oct')),
    (11, _('Nov')),
    (12, _('Dec')),
)


ORDINAL = (
    (1,  _('first')),
    (2,  _('second')),
    (3,  _('third')),
    (4,  _('fourth')),
    (-1, _('last'))
)

FREQUENCY_CHOICES = (
    (rrule.DAILY,   _('Day(s)')),
    (rrule.WEEKLY,  _('Week(s)')),
    (rrule.MONTHLY, _('Month(s)')),
    (rrule.YEARLY,  _('Year(s)')),
)

REPEAT_CHOICES = (
    ('count', _('By count')),
    ('until', _('Until date')),
)

ISO_WEEKDAYS_MAP = (
    None,
    rrule.MO,
    rrule.TU,
    rrule.WE,
    rrule.TH,
    rrule.FR,
    rrule.SA,
    rrule.SU
)

MINUTES_INTERVAL = swingtime_settings.TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = utils.time_delta_total_seconds(swingtime_settings.DEFAULT_OCCURRENCE_DURATION)


# IndexForm

class IndexForm(forms.Form):
    """
    Get the 3 main informations to print on the index page
    """

    #city = forms.ModelChoiceField(City.objects.all())
    quoi = forms.ModelChoiceField(
            EventType.objects.all(),
            required=False,
            empty_label=None,
            widget=forms.widgets.RadioSelect)

    quand = forms.DateField(
            required=True,
            initial=datetime.today(),
            widget=DateWidget(
                options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                },
                usel10n = True,
                bootstrap_version=3)
            )


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

# -------------------------------------------------------------------------------
def timeslot_offset_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT
):
    """
    Create a list of time slot options for use in swingtime forms.

    The list is comprised of 2-tuples containing the number of seconds since the
    start of the day and a 12-hour temporal representation of that offset.

    """
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    delta = utils.time_delta_total_seconds(dtstart - dt)
    seconds = utils.time_delta_total_seconds(interval)
    while dtstart <= dtend:
        options.append((delta, dtstart.strftime(fmt)))
        dtstart += interval
        delta += seconds

    return options

default_timeslot_options = timeslot_options()
default_timeslot_offset_options = timeslot_offset_options()

# ==============================================================================

class MultipleIntegerField(forms.MultipleChoiceField):
    """
    A form field for handling multiple integers.

    """

    #---------------------------------------------------------------------------
    def __init__(self, choices, size=None, label=None, widget=None):
        if widget is None:
            widget = forms.SelectMultiple(attrs={'size' : size or len(choices)})
        super(MultipleIntegerField, self).__init__(
            required=False,
            choices=choices,
            label=label,
            widget=widget,
        )

    #---------------------------------------------------------------------------
    def clean(self, value):
        return [int(i) for i in super(MultipleIntegerField, self).clean(value)]

# ==============================================================================

class EventForm(forms.ModelForm):
    """
    A simple form for adding and updating Event attributes

    """

     # ==========================================================================
    class Meta:
        model = Event
        if FIELDS_REQUIRED:
            fields = "__all__"
            #exclude = ['city']

    #---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(EventForm, self).__init__(*args, **kws)
        self.fields['description'].required = False


 # ==============================================================================

class SingleOccurrenceForm(forms.Form):
    """
    A simple form for adding and updating single Occurrence attributes
    # put request to true

    """
     # ==========================================================================
    date = forms.DateField(
        required=True,
        label=_('Date'),
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n = True,
            bootstrap_version=3)
        )


    start_time = forms.TimeField(
        required=True,
        label =_('Start time'),
        widget=TimeWidget(
            options={
                    'pickerPosition': 'top-left',
                    'minuteStep': 15,
                    },
            bootstrap_version=3)
        )


    end_time = forms.TimeField(
        required=False,
        label = _('End time'),
        widget=TimeWidget(
            options={
                    'pickerPosition': 'top-left',
                    'minuteStep': 15,
                    },
            bootstrap_version=3)
        )


    def clean(self):
        """
        :return: validation error if start_time or end_time in the past
        concatenate date and hour to give start and end datetime
        """
        cleaned_data = super(SingleOccurrenceForm, self).clean()
        start_time = datetime.combine(cleaned_data.get('date'), cleaned_data.get('start_time'))
        now = datetime.now()

        if start_time < now:
            raise forms.ValidationError("Verifier que la date correspond")

        if cleaned_data.get('end_time') is not None:
            end_time = datetime.combine(cleaned_data.get('date'), cleaned_data.get('end_time'))
            if start_time > end_time or end_time < now:
                raise forms.ValidationError("Verifier que les heures correspondent")

        return self.cleaned_data


    def save(self, event):
        """
        :param event:
        :return: end_time = start_time + 1h if end_time is None
        """
        start_time = datetime.combine(self.cleaned_data.get('date'), self.cleaned_data.get('start_time'))

        if self.cleaned_data.get('end_time') is not None:
            end_time = datetime.combine(self.cleaned_data.get('date'), self.cleaned_data.get('end_time'))
        else:
            end_time = start_time + timedelta(hours=1)

        event.add_occurrences(
            start_time,
            end_time,
            is_multiple=False,
        )

        return event


class MultipleOccurrenceForm(forms.Form):
    """
    Complex occurrences form
    """

    # frequency
    ## hour
    start_time_delta = forms.TimeField(
        label=_('Starting hour'),
        initial='14:00',
        widget=TimeWidget(
            options={'pickerPosition':'top-left',
                     'minuteStep':15,
                    },
            bootstrap_version=3)
        )

    end_time_delta = forms.TimeField(
        label=_('Ending hour'),
        initial='16:00',
        widget=TimeWidget(
            options={'pickerPosition':'top-left',
                     'minuteStep':15,
                    },
            bootstrap_version=3)
        )

    ## date options
    day = forms.DateField(
        label=_('From'),
        widget=DateWidget(
            options={
                    'todayHighlight':True,
                    'weekStart':1,
                    'pickerPosition':'top-left'
                    },
            usel10n = True,
            bootstrap_version=3)
        )


    until = forms.DateField(
        label=_('Until'),
        widget=DateWidget(
            options={
                    'todayHighlight':True,
                    'weekStart':1,
                    'pickerPosition':'top-left'
                    },
            usel10n = True,
            bootstrap_version=3)
        )


    ### weekly options
    week_days = MultipleIntegerField(
        WEEKDAY_SHORT,
        label=_('Weekly options'),
        widget=forms.CheckboxSelectMultiple
    )

    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(MultipleOccurrenceForm, self).__init__(*args, **kws)
        dtstart = self.initial.get('dtstart', None)
        if dtstart:
            dtstart = dtstart.replace(
                minute=((dtstart.minute // MINUTES_INTERVAL) * MINUTES_INTERVAL),
                second=0,
                microsecond=0
            )

            weekday = dtstart.isoweekday()

            self.initial.setdefault('day', dtstart)
            self.initial.setdefault('week_days', '%d' % weekday)

    # ---------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(MultipleOccurrenceForm, self).clean()
        start_time_delta = cleaned_data['start_time_delta']
        end_time_delta = cleaned_data['end_time_delta']
        day = cleaned_data['day']
        until = cleaned_data['until']

        if start_time_delta and end_time_delta:
            if start_time_delta > end_time_delta:
                raise forms.ValidationError("Verifier que les heures correspondent")

        if day and until:
            if day > until or day < date.today():
                raise forms.ValidationError("Verifier que les dates correspondent")

        self.cleaned_data['start_time'] = datetime.combine(day, start_time_delta)
        self.cleaned_data['end_time'] = datetime.combine(day, end_time_delta)

        return self.cleaned_data



    # ---------------------------------------------------------------------------
    def save(self, event):

        params = self._build_rrule_params()

        event.add_occurrences(
            self.cleaned_data['start_time'],
            self.cleaned_data['end_time'],
            is_multiple=True,
            **params
        )

        return event

    # ---------------------------------------------------------------------------
    def _build_rrule_params(self):

        data = self.cleaned_data
        params = dict(
            until=data['until'],
            byweekday=data['week_days'],
            interval=1,
            freq=rrule.WEEKLY,
        )

        return params