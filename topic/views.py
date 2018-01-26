# coding=utf-8
import calendar
from datetime import datetime, date, time

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from location.models import City
# TODO remove this asap
from crud import swingtime_settings

from . import utils
from .forms import IndexForm
from .models import Occurrence, EventType, Topic


# TODO remove this asap
if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


# -----------------------------------------------------------------------------
# index view
def index(request, topic_name, city_slug, template='topic/research.html'):
    """
    :param request:
    :param topic_name: name of the considered topic
    :param city_slug: slug of the current city
    :param template:
    :return: home template with index form
    """

    context = dict()
    topic = get_object_or_404(Topic, name=topic_name)
    city = get_object_or_404(City, city_slug=city_slug)

    if request.method == 'POST':
        form = IndexForm(topic, request.POST)

        if form.is_valid():
            # required
            query_date = form.cleaned_data['quand']
            # blank allowed
            event_type_list = form.cleaned_data['quoi']
            # hour by default else.
            start_hour = form.cleaned_data['start_hour']
            end_hour = form.cleaned_data['end_hour']

            if event_type_list:
                event_type_id_string = utils.create_id_string(event_type_list)
            else:
                event_type_id_string = utils.create_id_string(EventType.objects.filter(topic=topic))

            return redirect('location:topic:full_list',
                            start_year=query_date.year,
                            start_month=query_date.month,
                            start_day=query_date.day,
                            start_hour_string=utils.construct_hour_string(start_hour),
                            end_year=query_date.year,
                            end_month=query_date.month,
                            end_day=query_date.day,
                            end_hour_string=utils.construct_hour_string(end_hour),
                            event_type_id_string=event_type_id_string,
                            topic_name=topic_name,
                            city_slug=city.city_slug,
                            )

    else:
        form = IndexForm(topic)

    context['form'] = form
    context['topic'] = topic
    context['city'] = city

    return render(request, template, context)


# -----------------------------------------------------------------------------
# detail views
class OccurrenceDetail(DetailView):
    model = Occurrence
    template_name = "topic/single_event.html"

    def get_context_data(self, **kwargs):
        context = super(OccurrenceDetail, self).get_context_data(**kwargs)

        topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
        city = get_object_or_404(City, city_slug=self.kwargs['city_slug'])

        address = self.object.event.address
        # TODO improve this using location.address
        # if address == u'non précisé':
            # address += str(", " + str(self.request.site.name))

        # generic
        context['city'] = city
        context['topic'] = topic
        # side_bar
        context['all_event_type_list'] = EventType.objects.filter(topic=topic)

        context['address'] = address

        return context


# -----------------------------------------------------------------------------
# queries views

# mother function: event_type_list, start and end time
class DateList(ListView):
    """
    Queries occurrences in database from input kwargs and display them into 'topic/sorted_events.html' template

    input (as kwargs) in the url:
        - string, city_slug
        - string, topic_name
        - event_type_id_string: string, id of requested events
        - start_year
        - start_month
        - start_day
        - start_hour_string
        - end_year
        - end_month
        - end_day
        - end_hour_string

    return context:
        - all_event_type_list : for the sidebar
        - city: current location.models.City
        - topic: current topic.models.Topic
        - sorted_occurrences: list of topic.models.Occurrence
        - days: list of datetime.day corresponding to the time request
        - title: string, title of the page (requested event_types concatenation)
    """

    model = Occurrence
    template_name = 'topic/sorted_events.html'
    context_object_name = 'sorted_occurrences'

    # see https://docs.djangoproject.com/fr/2.0/topics/class-based-views/generic-display/
    def get_queryset(self):
        self.current_location = get_object_or_404(City, city_slug=self.kwargs['city_slug'])
        self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
        self.event_type_list = utils.get_event_type_list(self.kwargs['event_type_id_string'])

        start_date = utils.construct_day(self.kwargs['start_year'], self.kwargs['start_month'], self.kwargs['start_day'])
        start_hour = utils.construct_hour(self.kwargs['start_hour_string'])
        self.start_time = utils.construct_time(start_date, start_hour)

        end_date = utils.construct_day(self.kwargs['end_year'], self.kwargs['end_month'], self.kwargs['end_day'])
        end_hour = utils.construct_hour(self.kwargs['end_hour_string'])
        self.end_time = utils.construct_time(end_date, end_hour)

        sorted_occurrences = dict()
        for event_type in self.event_type_list:
            sorted_occurrences[event_type] = Occurrence.objects.filter(event__event_type=event_type,
                                                                       start_time__gte=self.start_time,
                                                                       end_time__lte=self.end_time,
                                                                       event__location=self.current_location,
                                                                       event__event_type__topic=self.topic,
                                                                       )
        return sorted_occurrences

    def get_context_data(self, **kwargs):
        context = super(DateList, self).get_context_data(**kwargs)
        # generic
        context['city'] = self.current_location
        context['topic'] = self.topic
        # side_bar
        context['all_event_type_list'] = EventType.objects.filter(topic=self.topic)
        # specific
        context['days'] = utils.list_days(self.start_time, self.end_time)
        context['title'] = ' - '.join([event.label for event in self.event_type_list])

        return context


# child functions
# city and topic already in context and query
# TODO maybe redirect to get all informations in url, instead of having all_events/today in url

# time queries
def today_all_events(request, **kwargs):
    start_time = datetime.combine(date.today(), time.min)
    end_time = datetime.combine(date.today(), time.max)
    topic = Topic.objects.get(name=kwargs['topic_name'])
    dic = utils.url_all_events_dict(topic, start_time, end_time)
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


def tomorrow_events(request, **kwargs):
    start_time = utils.tomorrow_morning()
    end_time = utils.tomorrow_evening()
    topic = Topic.objects.get(name=kwargs['topic_name'])
    dic = utils.url_all_events_dict(topic, start_time, end_time)
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


def coming_days_events(request, **kwargs):
    start_time = datetime.combine(date.today(), time.min)
    end_time = utils.end_of_next_days(duration=3)
    topic = Topic.objects.get(name=kwargs['topic_name'])
    dic = utils.url_all_events_dict(topic, start_time, end_time)
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


# event_type queries
def single_day_event_type_list(request, event_type_id_string, year, month, day, **kwargs):
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


def single_time_event_type_list(request,
                                event_type_id_string,
                                year, month, day,
                                start_hour_string,
                                end_hour_string,
                                **kwargs):
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, utils.construct_hour(start_hour_string))
    end_time = utils.construct_time(date_day, utils.construct_hour(end_hour_string))
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


def event_type_coming_days(request, event_type_id_string, **kwargs):
    start_time = datetime.now()
    end_time = utils.end_of_next_days(duration=3)
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)


def daily_events(request, year, month, day, **kwargs):
    d1 = {'event_type_id_string': utils.create_id_string(EventType.objects.all())}
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)
    dic = dict(utils.create_date_url_dict(start_time, end_time), **d1)
    kwargs = dict(dic, **kwargs)
    return DateList.as_view()(request, **kwargs)
