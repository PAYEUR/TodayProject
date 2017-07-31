# coding=utf-8

from __future__ import print_function, unicode_literals

from datetime import datetime, date, time, timedelta
from django.forms import formset_factory
from datetimewidget.widgets import DateWidget, TimeWidget
from dateutil import rrule
from django import forms
from location.models import City
from django.utils.translation import ugettext_lazy as _

from crud import swingtime_settings
from topic.models import Event, EventType, Topic

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

    # ---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(EventForm, self).__init__(*args, **kws)

        self.fields['location'] = forms.ModelChoiceField(
            City.objects.all(),
            label='Ville',
        )


# ==============================================================================
# Event type selection
class EventTypeByTopicForm(forms.Form):
    """
    Choosing event_types related to a topic. Need a topic as input data.
    """

    # ---------------------------------------------------------------------------
    def __init__(self, topic, *args, **kws):
        super(EventTypeByTopicForm, self).__init__(*args, **kws)

        self.topic = topic

        # need to have a prefix in order to properly select forms
        self.prefix = topic.name

        self.fields['event_type'] = forms.ModelChoiceField(
            queryset=EventType.objects.filter(topic=topic),
            label=self.topic.name,
            required=False,
            widget=forms.widgets.Select
            )

    def clean(self):
        """ if event_type field is blank, unvalid the form"""
        cleaned_data = super(EventTypeByTopicForm, self).clean()

        if not cleaned_data['event_type']:
            raise forms.ValidationError("Sélectionner la catégorie")

        return self.cleaned_data


class EventTypeByTopicFormsListManager:
    """
    Manager of a list of EventTypeByTopicForm.

    Has been written to shorten the view.
    Feature: if forms are not validated, all fields are set to initial state (instead of POST state) and form
    are presented again.

    initial_topic_forms: virgin list of EventTypeByTopicForms (served if request.method is not POST)
    only_one_form_error: boolean. False if exactly one form is validated. Used in context to print error text.
    request: input request
    topic_form_post: list of EventTypesByTopicForm served with POST data or None
    valid_topic_form: list of valid forms within topic_forms_post or None
    valid_form: the only valid EventTypeByTopicForm or None
    context: {"topic_forms" and "error"}

    """

    initial_topic_forms = [EventTypeByTopicForm(topic) for topic in Topic.objects.all()]
    only_one_form_error = False

    def __init__(self, request):
        self.request = request
        self.topic_forms_post = self.topic_forms_post()
        self.valid_topic_forms = self.get_valid_forms()
        #self.valid_form = self.check_valid_form()
        self.context = self.context()

    def topic_forms_post(self):
        """
        If request.method is POST, return a list of EventTypeByTopicForm bounded with post data. Else return None
        """
        if self.request.method == 'POST':
            return [EventTypeByTopicForm(topic, self.request.POST) for topic in Topic.objects.all()]
        else:
            return None

    def get_valid_forms(self):
        """get valid forms from a list of forms"""
        if self.topic_forms_post is not None:
            return [f for f in self.topic_forms_post if f.is_valid()]
        else:
            return None

    def check_valid_form(self):
        """
        Check if there is only one form valid within self.valid_topic_forms.
        If yes, set valid_form to this form
        If no, set None to valid_form and et only_one_form_error to True
        """
        if self.valid_topic_forms is not None:
            if len(self.valid_topic_forms) == 1:
                valid_form = self.valid_topic_forms[0]
            else:
                valid_form = None
                self.only_one_form_error = True
            return valid_form
        else:
            return None

    def context(self):
        """
        Returns the context for the view. Note that error is explicitely given into the context and not within a form.
        This is because EventTypeByTopicForm are hidden each others
        """
        context = {'topic_forms': self.initial_topic_forms,
                   'error': self.only_one_form_error,
                   }
        return context


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
        start_time = datetime.combine(self.cleaned_data.get('date'), self.cleaned_data.get('start_time'))

        if self.cleaned_data.get('end_time') is not None:  # TODO: specs have to clarify this
            end_time = datetime.combine(self.cleaned_data.get('date'), self.cleaned_data.get('end_time'))
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

            # test on hours
            if starting_hour > ending_hour:
                raise forms.ValidationError("Verifier que les heures correspondent")

            # test on days
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


class OccurrenceFormsListManager:
    # TODO: same EventTypeByTopicFormsListManager above but for MultipleOccurrenceForm and multiples dates

    SingleOccurrenceFormSet = formset_factory(SingleOccurrenceForm, extra=2, min_num=1, validate_min=True)
    initial_formset = SingleOccurrenceFormSet(prefix='single_occurrences')
    initial_multiple_occurrence_form = MultipleOccurrenceForm()
    only_one_form_error = False

    def __init__(self, request):
        self.request = request
        self.dates_forms_post = self.dates_forms_post()
        self.multiple_occurrence_form_post = self.multiple_occurrence_form_post()
        self.context = self.context()

    def dates_forms_post(self):
        """
        If request.method is POST, return a formset of SingleOccurrenceForm bounded with post data.
        Else return None
        """
        if self.request.method == 'POST':
            return self.SingleOccurrenceFormSet(self.request.POST, prefix='single_occurrences')
        else:
            return None

    def multiple_occurrence_form_post(self):
        """
        If request.method is POST, return a list of MultipleOccurrenceForm bounded with post data.
        Else return None
        """
        if self.request.method == 'POST':
            return MultipleOccurrenceForm(self.request.POST)
        else:
            return None

    def get_valid_form(self):
        """
        Check if there is only one form valid within a form list.
        If yes, set valid_form to this form
        If no, set None to valid_form and only_one_form_error to True
        """
        forms = [self.dates_forms_post, self.multiple_occurrence_form_post]

        valid_forms = [f for f in forms if f is not None and f.is_valid()]

        print("valid_forms: " + str(valid_forms))

        if len(valid_forms) == 1:
            return valid_forms[0]
        else:
            self.only_one_form_error = True
            return None

    def context(self):
        """
        Returns the context for the view. Note that error is explicitely given into the context and not within a form.
        This is because MultipleOccurenceForm and the Occurrence Formset Factory are hidding themselves.
        """
        context = {'initial_formset': self.initial_formset,
                   'initial_multiple_occurrence_form': self.initial_multiple_occurrence_form,
                   'error': self.only_one_form_error,
                   }
        return context



# TODO remove this
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

    prefix = 'multiple_date'

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