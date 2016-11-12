# coding=utf-8
import calendar
from datetime import datetime, date, time

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from core import swingtime_settings
from core.utils import get_current_topic
from . import utils
from .forms import IndexForm
from .models import Occurrence, EventType
from django.contrib.sites.models import Site
from django.views.decorators.cache import never_cache

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


def index(request, template='topic/research.html'):
    """
    :param request:
    :param template:
    :return: home template with index form
    """

    context = dict()
    topic = get_current_topic(request)

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

            return redirect(reverse('topic:single_time_event_type_list',
                                    kwargs={'year': query_date.year,
                                            'month': query_date.month,
                                            'day': query_date.day,
                                            'event_type_id_string': event_type_id_string,
                                            'start_hour_string': utils.construct_hour_string(start_hour),
                                            'end_hour_string': utils.construct_hour_string(end_hour),
                                            },
                                    current_app=topic.name),
                            )

    else:
        form = IndexForm(topic)

    context['form'] = form

    return render(request, template, context)


class OccurrenceDetail(DetailView):
    model = Occurrence
    template_name = "topic/single_event.html"

    def get_context_data(self, **kwargs):
        context = super(OccurrenceDetail, self).get_context_data(**kwargs)
        address = self.object.event.address
        # TODO improve this using location.address
        if address == u'non précisé':
            address += str(", " + str(self.request.site.name))

        context['address'] = address

        return context


# mother function
#@never_cache
def _get_events(request, event_type_list, start_time, end_time):

    # TODO: investigate this: some buggs probably due to cache
    Site.objects.clear_cache()
    current_site = Site.objects.get_current()
    Site.objects.clear_cache()

    topic = get_current_topic(request)
    title = ' - '.join([event.label for event in event_type_list])
    template = 'topic/sorted_events.html'

    sorted_occurrences = dict()

    for event_type in event_type_list:
        occurrences = Occurrence.objects.filter(event__event_type__topic=topic,
                                                event__site=current_site,
                                                event__event_type=event_type,
                                                start_time__gte=start_time,
                                                end_time__lte=end_time)
        sorted_occurrences[event_type] = occurrences

    context = dict({'sorted_occurrences': sorted_occurrences,
                    'days': utils.list_days(start_time, end_time),
                    'title': title
                    })

    return render(request, template, context)


# functions for date queries
def _all_events(request, start_time, end_time):
    event_type_list = EventType.objects.filter(topic=get_current_topic(request))
    return _get_events(request, event_type_list, start_time, end_time)


def today_events(request):
    print datetime.combine(date.today(), time.max)
    #TODO delete this start_time
    return _all_events(request, start_time=datetime.combine(date.today(), time.min), end_time=datetime.combine(date.today(), time.max))


def tomorrow_events(request):
    return _all_events(request, start_time=utils.tomorrow_morning(), end_time=utils.tomorrow_evening())


def coming_days_events(request):
    return _all_events(request, start_time=datetime.now(), end_time=utils.end_of_next_days(duration=3))


# functions for event_type queries

def single_day_event_type_list(request, event_type_id_string, year, month, day):
    event_type_list = utils.get_event_type_list(event_type_id_string, current_topic=get_current_topic(request))
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)

    return _get_events(request, event_type_list, start_time, end_time)


def single_time_event_type_list(request, event_type_id_string, year, month, day, start_hour_string, end_hour_string):
    event_type_list = utils.get_event_type_list(event_type_id_string, current_topic=get_current_topic(request))
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, utils.construct_hour(start_hour_string))
    end_time = utils.construct_time(date_day, utils.construct_hour(end_hour_string))

    return _get_events(request, event_type_list, start_time, end_time)


def event_type_coming_days(request, event_type_id_string):
    event_type_list = utils.get_event_type_list(event_type_id_string, current_topic=get_current_topic(request))
    start_time = datetime.now()
    end_time = utils.end_of_next_days(duration=3)

    return _get_events(request, event_type_list, start_time, end_time)


def daily_events(request, year, month, day):
    event_type_list = EventType.objects.filter(topic=get_current_topic(request))
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)

    return _get_events(request, event_type_list, start_time, end_time)
