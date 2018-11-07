# coding = utf-8
from __future__ import print_function, unicode_literals
import json
from datetime import datetime

from django.http import HttpResponse

from topic.models import Event, EventType
from location.models import City
from connection.models import EnjoyTodayUser
import utils


def update_external_events(request):

    # 1) reformat json file to make sure its encoding is utf-8
    # TODO

    # 2) read data
    with open('update_external_events/events_paris.json', 'r') as json_f:
        data = json.load(json_f)
        html_data = []
        for event in data['events']:

            # get event_types
            # TODO: match paris_tags with ET_event_type
            # for the moment set event_type = others by default
            event_types = []
            for tag in event['tags']:
                event_types.append(tag['label'])

            # create Event object:
            ET_event = Event()

            # by default
            ET_event.event_planner = EnjoyTodayUser.objects.get(user='admin')
            ET_event.event_type = EventType.objects.get(label='autres')
            ET_event.created_at = datetime.now()
            ET_event.location = City.objects.get(city_slug='paris')

            ET_event.image = event['image']
            ET_event.title = event['origin']['title']
            ET_event.public_transport = None
            ET_event.address = event['address']
            ET_event.contact = event['contributor']['organization']
            ET_event.price = event['conditions']['fr']
            ET_event.description = utils.set_event_description(event)

            ET_event.image_main = ET_event.image




            # get occurrences
            #if len(event['timings']) > 1:
                # event_is_multiple = True
            #for timing in event['timings']:
                #Event.add_occurrences()

            # create an ET event
            #event = Event()
            #events_title.append(event['title'])

        html = "<html><body>TITLES : %s.</body></html>" % str(html_data)
        return HttpResponse(html)

