from django.conf import settings
from django.views.generic import ListView
from core.utils import get_current_topic
from .models import Occurrence, EventType
from datetime import date, datetime, time, timedelta
#from django.shortcuts import get_object_or_404


def is_event_type_list(list):
    event_type_id_list = [event_type.id for event_type in EventType.objects.all()]
    for elt in list:
        if elt not in event_type_id_list:
            raise ValueError("'string' must be on event_type_list_string format")


def get_event_types(event_type_list_string):
    """unsplit event_type_list_string such as 1&2&3 into event_type_id and return corresponding EventTypes"""
    event_type_list = event_type_list_string.split('&')
    try:
        is_event_type_list(event_type_list)
    except ValueError:
        return EventType.objects.all()
    else:
        return EventType.objects.filter(id__in=list)


def convert_string_in_categories(string):
    # if string == 'toutes-categories':
        # return [EventType.objects.all()]
    # else:
        return get_event_types(string)


def convert_hour(hour_string):
    try:
        number = hour_string.split('h')
        return time(hour=number[0], minute=number[1])
    except ValueError:
        return None


class SortEvents(ListView):
    allow_empty = True
    context_object_name = 'occurrences'
    template_name = 'topic/event_by_date.html'

    def __init__(self,
                 event_type_list=EventType.objects.all(),
                 research_start_time=datetime.now(),
                 research_end_time=datetime.combine(date.today(), time.max),
                 *args,
                 **kwargs):

        super(SortEvents, self).__init__()
        self.event_type_list = event_type_list
        self.research_start_time = research_start_time
        self.research_end_time = research_end_time

    def construct_hours(self):
        # create day of the query
        try:
            start_day = datetime(int(self.kwargs['year']), int(self.kwargs['month']), int(self.kwargs['day']))
            if start_day == date.today():
                 self.research_start_time = datetime.now(),
                 self.research_end_time = datetime.combine(date.today(), time.max),
            else:
                self.research_start_time = datetime.combine(start_day, time.min)
                self.research_end_time = datetime.combine(start_day, time.max)
            try:
                start_hour = convert_hour(self.kwargs['start_hour'])
                end_hour = convert_hour(self.kwargs['end_hour'])
                self.research_start_time = datetime.combine(start_day, start_hour)
                self.research_end_time = datetime.combine(start_day, end_hour)
            except:
                pass
        except:
            pass

    def affect_event_type_list(self):
        if self.kwargs['event_type_id_string']:
            self.event_type_list = get_event_types(self.kwargs['event_type_id_string'])

    # query on the model
    def get_queryset(self):
        # qs = super(EventsInAPeriod, self).get_queryset()
        #qs = Occurrence.objects.all()
        current_topic = get_current_topic(self.request)
        site = settings.SITE_ID



        self.construct_hours()
        self.affect_event_type_list()
        #event_type_id_list = [event_type.pk for event_type in self.event_type_list]
        return Occurrence.objects.filter(event__event_type__topic=current_topic,
                         event__site=site,
                         event__event_type__in=self.event_type_list,
                         start_time__gte=self.research_start_time,
                         end_time__lte=self.research_end_time,
                         )

    def get_context_data(self, **kwargs):
        context = super(SortEvents, self).get_context_data(**kwargs)
        context['event_types_list'] = list(set([event.event_type for event in self.get_queryset()]))
        #TODO add an equivalent to [dt]??
        return context


class TomorrowEvents(SortEvents):
    tomorrow = date.today()+timedelta(days=+1)
    research_start_time = datetime.combine(tomorrow, time.min)


class NextDaysEvents(SortEvents):
    next_days_duration = 3
    end_day = date.today()+timedelta(days=+next_days_duration)
    research_end_time = datetime.combine(end_day, time.max)
