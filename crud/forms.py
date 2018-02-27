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
# TODO old features, remove this

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

    event_type = forms.ModelChoiceField(queryset=None,
                                        label="Catégorie",
                                        required=False,
                                        widget=forms.widgets.Select
                                        )

    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        # see https://stackoverflow.com/questions/1697702/how-to-pass-initial-parameter-to-djangos-modelform-instance
        topic = kws.pop('topic')
        super(EventTypeByTopicForm, self).__init__(*args, **kws)

        # reset queryset
        queryset = EventType.objects.filter(topic=topic)
        self.fields['event_type'].queryset = queryset

        self.prefix = topic.name
        self.href = '#' + self.prefix


# ==============================================================================
# Specified manager function
class FormsListManager:
    """
    Manager for lists of Forms or Formsets.

    """

    def __init__(self, *forms):
        self.forms = forms
        self.filled_forms = self.get_filled_forms()
        self.filled_form = self.get_filled_form()

    def get_filled_forms(self):
        """
            Check forms (resp. formsets) that have been modified and put them in filled_forms
        """
        filled_forms = [f for f in self.forms if f is not None and f.has_changed()]
        return filled_forms

    def get_filled_form(self):
        """
            If only one single form (resp formset) has been modified, put this form (resp formset) into filled_form.
        """
        if len(self.filled_forms) == 1:
            return self.filled_forms[0]
        else:
            return None


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
        label='Date de début',
        widget=DateWidget(
            options={
                    'todayHighlight': True,
                    'weekStart': 1,
                    'pickerPosition': 'top-left'
                    },
            usel10n=True,
            bootstrap_version=3)
        )

    end_date = forms.DateField(
        required=False,
        label='Date de fin',
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
        end_date = cleaned_data.get('end_date')  # [] if field is not filled
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not end_date:
            end_date = start_date

        # django uses "if" syntax instead of exception mechanism. See:
        # https: // docs.djangoproject.com / fr / 2.0 / ref / forms / validation /
        if start_date and start_time and end_time:

            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            # 1st condition: invalid date
            if start_datetime < datetime.now():
                raise forms.ValidationError("Verifier que la date correspond")

            # 2nd condition: invalid_time
            if start_datetime > end_datetime:
                raise forms.ValidationError("Verifier que les heures correspondent")

            else:
                self.start_datetime = start_datetime
                self.end_datetime = end_datetime

    def save(self, event):
        """
        :param event: Event object
        :return: Save event in DB linked with current occurrences and return event.
        """

        event.add_occurrences(
            self.start_datetime,
            self.end_datetime,
            is_multiple=False,
        )

        return event


class MultipleOccurrenceForm(forms.Form):
    """
    Complex occurrences form
    """

    # ----------------------------------------------------------------------------
    # fields

    start_time = forms.TimeField(
        label='Horaire de début',
        #initial='14:00',
        widget=TimeWidget(
            options={'pickerPosition': 'top-left',
                     'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    end_time = forms.TimeField(
        required=True,
        label='Horaire de fin',
        #initial='22:30',
        widget=TimeWidget(
            options={'pickerPosition': 'top-left',
                     'minuteStep': 15,
                    },
            bootstrap_version=3)
        )

    start_date = forms.DateField(
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

    end_date = forms.DateField(
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

    week_days = MultipleIntegerField(
        WEEKDAY_LONG,
        label='Jours de la semaine',
        widget=forms.CheckboxSelectMultiple
    )

    # -----------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(MultipleOccurrenceForm, self).clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        week_days = cleaned_data.get('week_days')

        if start_time and end_time and start_date and end_date and week_days:

            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            # 1st condition
            if start_datetime > end_datetime or end_datetime < datetime.now():
                raise forms.ValidationError("Verifier que la date correspond")

            # 2nd condition
            if start_datetime > end_datetime:
                raise forms.ValidationError("Verifier que les heures correspondent")

            self.start_datetime = start_datetime
            self.end_datetime = end_datetime

            return self.cleaned_data

    # ---------------------------------------------------------------------------
    def save(self, event):

        params = self._build_rrule_params()

        event.add_occurrences(
            self.start_datetime,
            self.end_datetime,
            is_multiple=True,
            **params
        )

        return event

    # ---------------------------------------------------------------------------
    def _build_rrule_params(self):

        data = self.cleaned_data
        params = dict(
            until=data['end_date'],
            byweekday=data['week_days'],
            interval=1,
            freq=rrule.WEEKLY,
        )

        return params
