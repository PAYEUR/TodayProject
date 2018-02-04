# coding=utf-8

from __future__ import print_function, unicode_literals

from datetime import datetime, date, time, timedelta
from datetimewidget.widgets import DateWidget, TimeWidget
from dateutil import rrule
from django import forms
from location.models import City
from django.utils.translation import ugettext_lazy as _

from crud import swingtime_settings
from topic.models import Event, EventType

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


# ===============================================================================
# TOD0 old features, remove this

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

    # ---------------------------------------------------------------------------
    def clean(self, value):
        return [int(i) for i in super(MultipleIntegerField, self).clean(value)]


# ==============================================================================
# Event creation form
class EventForm(forms.ModelForm):
    """
    A simple form for adding and updating Event attributes.
    """

    class Meta:
        model = Event
        fields = ['image',
                  'title',
                  'description',
                  'price',
                  'contact',
                  'address',
                  'public_transport',
                  'location',
                  ]

    # TODO: add event_type here instead of locating it in an outside form
    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(EventForm, self).__init__(*args, **kws)

        self.fields['location'] = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label='Ville',
        )


# ==============================================================================
# Event type selection
class EventTypeByTopicForm(forms.Form):
    """
    Choosing event_types related to a topic. Need a topic as input data.
    see https://docs.djangoproject.com/fr/2.0/topics/forms/formsets/#passing-custom-parameters-to-formset-forms
    """

    event_type = forms.ModelChoiceField(queryset=EventType.objects.all(),
                                        label="Catégorie",
                                        required=True,
                                        widget=forms.widgets.Select
                                        )

    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        # see https://stackoverflow.com/questions/1697702/how-to-pass-initial-parameter-to-djangos-modelform-instance
        topic = kws.pop('topic')
        super(EventTypeByTopicForm, self).__init__(*args, **kws)

        # need to have a prefix in order to properly select forms
        self.prefix = topic.name
        self.href = '#' + self.prefix

        self.fields['event_type'].queryset = EventType.objects.filter(topic=topic)


# ==============================================================================
# Specified manager function
class FormsListManager:
    """
    Manager for lists of Forms or Formsets.

    """

    def __init__(self):
        self.filled_forms = []
        self.filled_form = None
        self.error = False

    def check_filled_forms(self, forms):
        """
            Check forms (resp. formsets) that have been modified and put them in filled_forms
        """

        filled_forms = [f for f in forms if f is not None and f.has_changed()]
        self.filled_forms = filled_forms

    def only_one_form_is_filled(self):
        """
            Assert if one single form (resp. formset) has been modified.
        """
        return len(self.filled_forms) == 1

    def set_filled_form(self):
        """
            If only one single form (resp formset) has been modified, put this form (resp formset) into filled_form.
        """
        if self.only_one_form_is_filled():
            self.filled_form = self.filled_forms[0]


# ==============================================================================
# Occurrence forms creation
class SingleOccurrenceForm(forms.Form):
    """
    A simple form for adding and updating single Occurrence attributes
    # put request to true

    """
    # ==========================================================================
    start_date = forms.DateField(
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
        cleaned_data = super(SingleOccurrenceForm, self).clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_date and start_time and end_time:

            start_time = datetime.combine(start_date, start_time)
            end_time = datetime.combine(start_date, end_time)
            now = datetime.now()

            # 1st condition
            if start_time < now:
                raise forms.ValidationError("Verifier que la date correspond")

            # 2nd condition
            if start_time > end_time or end_time < now:
                raise forms.ValidationError("Verifier que les heures correspondent")

            return self.cleaned_data

    def save(self, event):
        """
        :param event:
        :return: end_time = start_time + 1h if end_time is None
        """
        start_time = datetime.combine(self.cleaned_data.get('start_date'), self.cleaned_data.get('start_time'))

        if self.cleaned_data.get('end_time') is not None:  # TODO: specs have to clarify this
            end_time = datetime.combine(self.cleaned_data.get('start_date'), self.cleaned_data.get('end_time'))
        else:
            end_time = start_time + timedelta(hours=1)

        event.add_occurrences(
            start_time,
            end_time,
            is_multiple=False,  # TODO: remove this feature
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
        #initial='14:00',
        widget=TimeWidget(
            options={'pickerPosition': 'top-left',
                     'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    ending_hour = forms.TimeField(
        required=True,
        label='Horaire de fin',
        #initial='22:30',
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
        #initial=date.today,
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
        #initial=date(date.today().year, 12, 31),
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

    prefix = 'multiple_occurrence'

    def clean(self):
        cleaned_data = super(MultipleOccurrenceForm, self).clean()
        starting_hour = cleaned_data.get('starting_hour')
        ending_hour = cleaned_data.get('ending_hour')
        start_day = cleaned_data.get('start_day')
        end_day = cleaned_data.get('end_day')

        if starting_hour and ending_hour and start_day and end_day:

            start_time = datetime.combine(start_day, starting_hour)
            end_time = datetime.combine(end_day, ending_hour)
            now = datetime.now()

            # 1st condition
            if start_time > end_time or end_time < now:
                raise forms.ValidationError("Verifier que la date correspond")

            # 2nd condition
            if starting_hour > ending_hour:
                raise forms.ValidationError("Verifier que les heures correspondent")

            self.cleaned_data['first_day_start_time'] = start_time
            self.cleaned_data['first_day_end_time'] = end_time

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
