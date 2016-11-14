# coding=utf-8

from __future__ import print_function, unicode_literals

from datetime import datetime, date, time, timedelta

from datetimewidget.widgets import DateWidget, TimeWidget
from dateutil import rrule
from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from core import swingtime_settings
from topic.models import Event, EventType  #,City, Occurrence

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


# ==============================================================================

class MultipleIntegerField(forms.MultipleChoiceField):
    """
    A form field for handling multiple integers.

    """

    # ---------------------------------------------------------------------------
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
        fields = "__all__"
        exclude = ['event_planner', 'objects', 'on_site']


    # ---------------------------------------------------------------------------
    def __init__(self, topic, *args, **kws):
        super(EventForm, self).__init__(*args, **kws)
        self.topic = topic

        self.fields['event_type'] = forms.ModelChoiceField(
            EventType.objects.filter(topic=topic),
            label='Catégorie',
            #required=False,
            empty_label=None,
            widget=forms.widgets.Select)

        # TODO print name of the city instead of the domain_name
        self.fields['site'] = forms.ModelChoiceField(
            Site.objects.exclude(name__contains='oday'),
            label='Site internet de la ville sur lequel sera posté l\'événement',
            #to_field_name="name"  # doesn't work...
        )


# ==============================================================================


class SingleOccurrenceForm(forms.Form):
    """
    A simple form for adding and updating single Occurrence attributes
    # put request to true

    """
    # ==========================================================================
    date = forms.DateField(
        required=True,
        initial=date.today,
        label='Date',
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n=True,
            bootstrap_version=3)
        )

    start_time = forms.TimeField(
        required=True,
        initial='14:00',
        label='Horaire de début',
        widget=TimeWidget(
            options={
                    'pickerPosition': 'top-left',
                    'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    end_time = forms.TimeField(
        required=True,
        initial='22:30',
        label='Horaire de fin',
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
    starting_hour = forms.TimeField(
        label='Horaire de début',
        initial='14:00',
        widget=TimeWidget(
            options={'pickerPosition': 'top-left',
                     'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    ending_hour = forms.TimeField(
        required=True,
        label='Horaire de fin',
        initial='22:30',
        widget=TimeWidget(
            options={'pickerPosition': 'top-left',
                     'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    ## date options
    start_day = forms.DateField(
        required=True,
        label='A partir du',
        initial=date.today,
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n=True,
            bootstrap_version=3)
        )


    end_day = forms.DateField(
        required=True,
        label='Jusqu\'au',
        initial=date(date.today().year, 12, 31),
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n=True,
            bootstrap_version=3)
        )


    ### weekly options
    week_days = MultipleIntegerField(
        WEEKDAY_LONG,
        label='Jours de la semaine',
        widget=forms.CheckboxSelectMultiple
    )

    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        """
        :param args:
        :param kws:
        :return: prefilling widget with current time. (not ultra useful)
        """
        super(MultipleOccurrenceForm, self).__init__(*args, **kws)
        dtstart = self.initial.get('dtstart', None)
        if dtstart:
            dtstart = dtstart.replace(
                minute=((dtstart.minute // MINUTES_INTERVAL) * MINUTES_INTERVAL),
                second=0,
                microsecond=0
            )

            self.initial.setdefault('start_day', dtstart)
            self.initial.setdefault('week_days', '%d' % dtstart.isoweekday())

    # ---------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(MultipleOccurrenceForm, self).clean()
        starting_hour = cleaned_data['starting_hour']
        ending_hour = cleaned_data['ending_hour']
        start_day = cleaned_data['start_day']
        end_day = cleaned_data['end_day']

        if starting_hour and ending_hour:
            if starting_hour > ending_hour:
                raise forms.ValidationError("Verifier que les heures correspondent")

        if start_day and end_day:
            if start_day > end_day or start_day < date.today():
                raise forms.ValidationError("Verifier que les dates correspondent")
            # pas de test si un événement est créé aujourd'hui mais à une heure déjà passée

        self.cleaned_data['first_day_start_time'] = datetime.combine(start_day, starting_hour)
        self.cleaned_data['first_day_end_time'] = datetime.combine(start_day, ending_hour)

        return self.cleaned_data

    # ---------------------------------------------------------------------------
    def save(self, event):

        params = self._build_rrule_params()

        event.add_occurrences(
            self.cleaned_data['first_day_start_time'],
            self.cleaned_data['first_day_end_time'],
            is_multiple=True,
            **params
        )

        return event

    # ---------------------------------------------------------------------------
    def _build_rrule_params(self):

        data = self.cleaned_data
        params = dict(
            until=data['end_day'],
            byweekday=data['week_days'],
            interval=1,
            freq=rrule.WEEKLY,
        )

        return params


# ==============================================================================
# TODO merge this with other forms
## form that allows letting date and hours not filled for multiple date form

class MultipleDateSingleOccurrenceForm(forms.Form):
    """
    A simple form for adding and updating single Occurrence attributes
    # put request to true

    """
    # ==========================================================================
    date = forms.DateField(
        required=True,
        #initial=date.today,
        label='Date',
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n=True,
            bootstrap_version=3)
        )

    start_time = forms.TimeField(
        required=True,
        #initial='14:00',
        label='Horaire de début',
        widget=TimeWidget(
            options={
                    'pickerPosition': 'top-left',
                    'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    end_time = forms.TimeField(
        required=True,
        #initial='22:30',
        label='Horaire de fin',
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
        cleaned_data = super(MultipleDateSingleOccurrenceForm, self).clean()
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