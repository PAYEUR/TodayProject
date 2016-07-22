import calendar
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
from .forms import IndexForm
from .models import EventType, Occurrence, Event, EnjoyTodayUser
from django.views.generic import DetailView, DayArchiveView, ListView

# from django.views.generic.detail import SingleObjectMixin
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.template import RequestContext
from . import swingtime_settings
from django.conf import settings
from core.utils import get_current_topic


if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)


def index(request, template='topic/research.html', **kwargs):
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
            # dont use city from now
            event_type_list = form.cleaned_data['quoi']
            print event_type_list is False
            event_type_id_string = '&'.join([str(event_type.id) for event_type in event_type_list])
            date = form.cleaned_data['quand']

            if event_type_list:
                return redirect(reverse('topic:single_day_event_type_list',
                                        kwargs={'year': date.year,
                                            'month': date.month,
                                            'day': date.day,
                                            'event_type_id_string': event_type_id_string
                                            },
                                    current_app=topic.name),
                                )

            else:
                return redirect(reverse('topic:daily_events',
                                    current_app=topic.name,
                                    kwargs={'year': date.year,
                                            'month': date.month,
                                            'day': date.day,
                                            }
                                    ))

    else:
        form = IndexForm(topic)

    context['form'] = form

    return render(request, template, context)


class OccurrenceDetail(DetailView):
    model = Occurrence
    template_name = "topic/single_event.html"

    def get_context_data(self, **kwargs):
        context = super(OccurrenceDetail, self).get_context_data(**kwargs)
        #TODO improve this using location.address
        if self.object.event.address != "non precise":
            address = self.object.event.address + ", France"
        else:
            address = False
        context['address'] = address

        return context


#---------------------------------------------------------------------------------------------------------------
## Events sorted by date

# queryset has to be properly written to take date and hour into account
# unused
class EventsInAPeriod(ListView):
    allow_empty = True
    queryset = Occurrence.objects.all()
    context_object_name = 'occurrences'
    template_name = 'topic/event_by_date.html'
    # fix it depending on the request
    # start_time = datetime.now()
    # end_time = datetime.now() + timedelta(hours=200)


    # query on the model
    def get_queryset(self):
       qs = super(EventsInAPeriod, self).get_queryset()
       return qs.filter(event__event_type__topic=get_current_topic(self.request),
                        event__site=settings.SITE_ID)


    def get_context_data(self, **kwargs):
       context = super(EventsInAPeriod, self).get_context_data(**kwargs)
       context['event_types_list']= list(set([event.event_type for event in self.get_queryset()]))
       return context



def _events_in_a_period(request,
                        days,
                        template='topic/event_by_date.html',
                       ):
    """

    :param request:
    :param days: a list of days
    :return: context with occurrences, event_types_list and days
    """
    # not satisfying because len(moment) times database requests

    # print event_types occurrences
    # TODO: verify the following point: if no event at all in coming days => crash?!

    topic = get_current_topic(request)
    site_id = settings.SITE_ID

    occurrences = []
    for day in days:

        occurrences_day = Occurrence.objects.daily_occurrences(dt=day).filter(event__site=site_id,
                                                                     event__event_type__topic=topic)

        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    # get all related event_types  (double sorted)
    events_list = [occurrence.event for occurrence in occurrences]
    event_types_list = list(set([event.event_type for event in events_list]))

    context = dict({'occurrences': occurrences,
                   'event_types_list': event_types_list,
                    'days': days,

                    })

    return render(request, template, context)


def today_events(request,
                 template='topic/event_by_date.html',
                 ):
    """

    :param request:
    :param template:
    :return: all events for topic
    """
    days = [datetime.today()]

    return _events_in_a_period(request, days, template)


def tomorrow_events(request,
                    template='topic/event_by_date.html',
                    ):
    """

    :param request:
    :param template:
    :return: all events for tomorrow
    """
    days = [datetime.today() + timedelta(days=+1)]

    return _events_in_a_period(request, days, template)


def coming_days_events(request,
                       next_days_duration=3,
                       template='topic/event_by_date.html',
                       ):
    """

    :param request:
    :param next_days_duration: how many days does "coming_days" mean
    :param template:
    :return: all events for coming_days
    """
    today = datetime.now()
    i = 0
    days = []
    while i < int(next_days_duration):
        days.append(today + timedelta(days=+i))
        i += 1

    return _events_in_a_period(request, days, template)


def daily_events(request,
                 year,
                 month,
                 day,
                 template='topic/event_by_date.html',
                 ):

    days = [datetime(int(year), int(month), int(day))]

    return _events_in_a_period(request, days, template)


def monthly_events(request,
                   year,
                   month,
                   template='topic/event_by_date.html',
                  ):

    year, month = int(year), int(month)
    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(year, month)
    days = []
    for week in weeks:
        for day in week:
            days.append(day)


    return _events_in_a_period(request, days, template)


def event_type_coming_days(request,
                           event_type_id,
                           next_days_duration=3,
                           template='topic/date_by_event_type.html',
                           ):
    """

    :param request:
    :param event_type_id:
    :param next_days_duration:
    :param template:
    :return: every occurrences of a single event_type within next_days_duration days
    """

    # list of next_day_duration days
    today = datetime.now()
    i = 0
    days = []
    while i < int(next_days_duration):
        days.append(today + timedelta(days=+i))
        i += 1

    # sort event_type.occurrences by day
    event_type = get_object_or_404(EventType, pk=int(event_type_id))
    topic= get_current_topic(request)
    occurrences = []
    for day in days:
        occurrences_day = Occurrence.objects.daily_occurrences(dt=day).filter(event__event_type=event_type,
                                                                              event__site=settings.SITE_ID,
                                                                              event__event_type__topic=topic)
        for occurrence_day in occurrences_day:
            occurrences.append(occurrence_day)

    context = dict({'occurrences': occurrences,
                    'event_type': event_type,

                    }
                   )

    return render(request, template, context)


#--------------------------------------------------------------------------------------------------------------
#  Events sorted by event_type
def _single_day_event_type(
        request,
        event_type_list,
        dt,
        template='topic/event_by_date.html',

        ):

    #event_type_list = get_list_or_404(EventType.objects.filter(pk__in=event_type_id_list))
    occurrences = Occurrence.objects.daily_occurrences(dt=dt).filter(event__event_type__in=event_type_list)

    context = dict({'occurrences': occurrences,
                    'event_types_list': event_type_list,
                    'days': [dt],

                    }
                   )

    return render(request, template, context)


def single_day_event_type_list(
        request,
        event_type_id_string,
        year,
        month,
        day,
        template='topic/event_by_date.html',
        ):

    dt = datetime(int(year), int(month), int(day))
    event_type_id_list = event_type_id_string.split('&')
    event_type_list=[EventType.objects.get(id=id) for id in event_type_id_list]
    return _single_day_event_type(request, event_type_list, dt, template)


# Non used
def today_event_type(
        request,
        event_type_list,
        template='topic/event_by_date.html',

        ):

    dt = datetime.today()
    return _single_day_event_type(request, event_type_list, dt, template,)

# Non used
def tomorrow_event_type(
        request,
        event_type_list,
        template='topic/event_by_date.html',

        ):

    dt = datetime.today()+timedelta(days=+1)
    return _single_day_event_type(request, event_type_list, dt, template, )


# non used
def single_day_event_type(
        request,
        event_type_id,
        year,
        month,
        day,
        template='topic/event_by_date.html',
        ):

    dt = datetime(int(year), int(month), int(day))
    return _single_day_event_type(request,
                                  [EventType.objects.get(pk=event_type_id)],
                                  dt,
                                  template)

#---------------------------------------------------------------------------------------------------------------
# Event_choice


