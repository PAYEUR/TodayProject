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


from django.http import HttpResponse

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


def test1(request, topic_name, city_slug):
    # test if kwargs are correctly taken into account
    return HttpResponse("sujet : " + str(topic_name) + " ;  Ville : " + str(city_slug))


def test2(request, topic_name, city_slug):
    # tests if a template can be rendered
    context = {'title': topic_name + " a " + city_slug,
               'site': City.objects.get(city_slug=city_slug),
               }
    return render(request, template_name='topic/test.html', context=context)


# on suppose la ville et le topic connus
def index(request, topic_name, city_slug, template='topic/research.html'):
    """
    :param request:
    :param template:
    :return: home template with index form
    """

    context = dict()
    topic =  get_object_or_404(Topic, name=topic_name)

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

            return redirect(reverse('DateList.as_view()',
                                    kwargs={'start_year': query_date.year,
                                            'start_month': query_date.month,
                                            'start_day': query_date.day,
                                            'start_hour_string': utils.construct_hour_string(start_hour),
                                            'end_year': query_date.year,
                                            'end_month': query_date.month,
                                            'end_day': query_date.day,
                                            'end_hour_string': utils.construct_hour_string(end_hour),
                                            'event_type_id_string': event_type_id_string,
                                            'topic_name': topic_name,
                                            'city_slug': city_slug,
                                            },
                                    )
                            )

    else:
        form = IndexForm(topic)

    context['form'] = form

    return render(request, template, context)


# -----------------------------------------------------------------------------
# detail views

class OccurrenceDetail(DetailView):
    model = Occurrence
    template_name = "topic/single_event.html"

    def get_context_data(self, **kwargs):
        context = super(OccurrenceDetail, self).get_context_data(**kwargs)
        address = self.object.event.address
        # TODO improve this using location.address
        # if address == u'non précisé':
            # address += str(", " + str(self.request.site.name))

        context['address'] = address

        return context


# -----------------------------------------------------------------------------
# queries views

# grand-mother function: topic and city
class LocationTopicList(ListView):

    model = Occurrence
    template_name = 'topic/sorted_events.html'
    context_object_name = 'sorted_occurrences'

    def get_queryset(self):
        self.current_location = get_object_or_404(City, city_slug=self.kwargs['city_slug'])
        self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])

        return Occurrence.objects.filter(event__location=self.current_location,
                                         event__event_type__topic=self.topic,
                                         )

    def get_context_data(self, **kwargs):
        context = super(LocationTopicList, self).get_context_data(**kwargs)
        context['city'] = self.current_location
        context['topic'] = self.topic
        return context


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
        - sorted_occurrences: list of topic.models.Occurrence
        - city: current location.models.City
        - topic: current topic.models.Topic
        - days: list of datetime.day corresponding to the time request
        - title: string, title of the page (requested event_types concatenation)
    """

    model = Occurrence
    template_name = 'topic/sorted_events.html'
    context_object_name = 'sorted_occurrences'

    def get_queryset(self):
        #queryset = super(DateList, self).get_context_data()
        self.current_location = get_object_or_404(City, city_slug=self.kwargs['city_slug'])
        self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
        self.event_type_list = utils.get_event_type_list(self.kwargs['event_type_id_string'])

        start_date = utils.construct_day(self.kwargs['start_year'], self.kwargs['start_month'], self.kwargs['start_day'])
        start_hour = utils.construct_hour(self.kwargs['start_hour_string'])
        self.start_time = utils.construct_time(start_date, start_hour)

        end_date = utils.construct_day(self.kwargs['end_year'], self.kwargs['end_month'], self.kwargs['end_day'])
        end_hour = utils.construct_hour(self.kwargs['end_hour_string'])
        self.end_time = utils.construct_time(end_date, end_hour)

        return Occurrence.objects.filter(event__event_type__in=self.event_type_list,
                               start_time__gte=self.start_time,
                               end_time__lte=self.end_time,
                                         event__location=self.current_location,
                                         event__event_type__topic=self.topic,
                               )

    def get_context_data(self, **kwargs):
        context = super(DateList, self).get_context_data(**kwargs)
        context['days'] = utils.list_days(self.start_time, self.end_time)
        context['title'] = ' - '.join([event.label for event in self.event_type_list])
        context['city'] = self.current_location
        context['topic'] = self.topic

        return context

# child functions
def today_all_events(request, **kwargs):
    # normally city and topic are already in request.
    start_time = datetime.combine(date.today(), time.min)
    end_time = datetime.combine(date.today(), time.max)
    dic = utils.url_all_events_dict(start_time, end_time)
    kwargs = dict(dic, **kwargs)
    #dic2 ={'city_slug':"paris", 'topic_name':"spi"}
    return DateList.as_view()(request, **kwargs)



def tomorrow_events(request):
    start_time = utils.tomorrow_morning()
    end_time = utils.tomorrow_evening()
    dic = utils.url_all_events_dict(start_time, end_time)
    return redirect('DateList.as_view()', dic)


def coming_days_events(request):
    start_time = datetime.combine(date.today(), time.min)
    end_time = utils.end_of_next_days(duration=3)
    dic = utils.url_all_events_dict(start_time, end_time)
    return redirect('DateList.as_view()', dic)


# functions for event_type queries
def single_day_event_type_list(request, event_type_id_string, year, month, day):
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    return redirect('DateList.as_view()', dic)


def single_time_event_type_list(request, event_type_id_string, year, month, day, start_hour_string, end_hour_string, **kwargs):
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, utils.construct_hour(start_hour_string))
    end_time = utils.construct_time(date_day, utils.construct_hour(end_hour_string))
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    kwargs = dict(dic, **kwargs)
    return redirect('DateList.as_view()', **kwargs)


def event_type_coming_days(request, event_type_id_string):
    start_time = datetime.now()
    end_time = utils.end_of_next_days(duration=3)
    dic = dict(utils.create_date_url_dict(start_time, end_time), **{'event_type_id_string': event_type_id_string})
    return redirect('DateList.as_view()', dic)


def daily_events(request, year, month, day):
    d1 = {'event_type_id_string': utils.create_id_string(EventType.objects.all())}
    date_day = utils.construct_day(year, month, day)
    start_time = utils.construct_time(date_day, time.min)
    end_time = utils.construct_time(date_day, time.max)
    dic = dict(utils.create_date_url_dict(start_time, end_time), d1)
    return redirect('DateList.as_view()', dic)
