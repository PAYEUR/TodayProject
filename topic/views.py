# coding=utf-8
import calendar
from datetime import datetime, date, time

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from location.models import City
from core import swingtime_settings
from . import utils
from .forms import IndexForm
from .models import Occurrence, EventType, Topic

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


#TODO: where is the mention of city here?
def index(request, topic_name, template='topic/research.html'):
    """
    :param request:
    :param template:
    :return: home template with index form
    """

    context = dict()
    topic = get_object_or_404(Topic, name=topic_name)

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


# -----------------------------------------------------------------------------
# queries views
# mother function
def _get_events(request, event_type_list, city_slug, topic_name, start_time, end_time):

    current_location = get_object_or_404(City, city_slug=city_slug)
    topic = get_object_or_404(Topic, name=topic_name)

    title = ' - '.join([event.label for event in event_type_list])
    template = 'topic/sorted_events.html'

    sorted_occurrences = dict()

    for event_type in event_type_list:
        occurrences = Occurrence.objects.filter(event__event_type__topic=topic,
                                                event__location=current_location,
                                                event__event_type=event_type,
                                                start_time__gte=start_time,
                                                end_time__lte=end_time)
        sorted_occurrences[event_type] = occurrences

    context = dict({'sorted_occurrences': sorted_occurrences,
                    'days': utils.list_days(start_time, end_time),
                    'title': title
                    })

    return render(request, template, context)


# # another way to write it
# class LocationTopicList(ListView):
#
#     template = 'topic/sorted_events.html'
#     context_object_name = 'sorted_occurrences'
#     start_time = datetime.now()
#     end_time = utils.end_of_next_days(duration=3)
#
#     def get_queryset(self):
#         self.current_location = get_object_or_404(City, city_slug=self.kwargs['city_slug'])
#         self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
#         return Occurrence.objects.filter(event__location=self.current_location,
#                                          event__event_type__topic=self.topic,
#                                          start_time__gte=self.start_time,
#                                          end_time__lte=self.end_time,
#                                          )
#
#     def get_context_data(self, **kwargs):
#         context = super(LocationTopicList, self).get_context_data(**kwargs)
#         context['days'] = utils.list_days(self.start_time, self.end_time)
#         context['title'] = "toutes catégories"
#
#
# class TodayList(LocationTopicList):
#
#     start_time = datetime.combine(date.today(), time.min)
#     end_time = datetime.combine(date.today(), time.max)
#
#
# class TomorrowList(LocationTopicList):
#
#     start_time = datetime.combine(date.tomorrow(), time.min)
#     end_time = datetime.combine(date.tomorrow), time.max)
#
# class SingleDayList(LocationTopicList):
#
# self.event_type_list = utils.get_event_type_list(self.kwargs['event_type_id_string'])
#         return Occurrence.objects.filter(event__location=self.current_location,
#                                          event__event_type__topic=self.topic,
#                                          event__event_type__in=self.event_type_list,
#                                          start_time__gte=self.start_time,
#                                          end_time__lte=self.end_time,
#                                          )

#' - '.join([event.label for event in self.event_type_list])

# functions for date queries
def _all_events(request, start_time, end_time):
    event_type_list = EventType.objects.all()
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
    event_type_list = utils.get_event_type_list(event_type_id_string)
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)

    return _get_events(request, event_type_list, start_time, end_time)


def single_time_event_type_list(request, event_type_id_string, year, month, day, start_hour_string, end_hour_string):
    event_type_list = utils.get_event_type_list(event_type_id_string)
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, utils.construct_hour(start_hour_string))
    end_time = utils.construct_time(date_day, utils.construct_hour(end_hour_string))

    return _get_events(request, event_type_list, start_time, end_time)


def event_type_coming_days(request, event_type_id_string):
    event_type_list = utils.get_event_type_list(event_type_id_string)
    start_time = datetime.now()
    end_time = utils.end_of_next_days(duration=3)

    return _get_events(request, event_type_list, start_time, end_time)


def daily_events(request, year, month, day):
    event_type_list = EventType.objects.all()
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)

    return _get_events(request, event_type_list, start_time, end_time)
