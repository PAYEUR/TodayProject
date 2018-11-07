# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import json
from datetime import datetime

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from topic.models import Event, EventType, Occurrence
from location.models import City
from connection.models import EnjoyTodayUser
import utils


def update_external_events(request):

    # 1) reformat json file to make sure its encoding is utf-8
    # TODO

    # 2) read data
    with open('update_external_events/events_paris.json', 'r') as json_f:
        data = json.load(json_f)
        new_events = []
        updated_events = []
        for event in data['events']:

            # get event_types
            # TODO: match paris_tags with ET_event_type
            # for the moment set event_type = others by default
            event_types = []
            for tag in event['tags']:
                event_types.append(tag['label'])

            # create Event object:
            ET_event = Event()

            ## by default
            ET_event.event_planner = EnjoyTodayUser.objects.get(user__username='admin')
            ET_event.event_type = EventType.objects.get(label='autres')
            ET_event.created_at = datetime.now()
            ET_event.location = City.objects.get(city_slug='paris')

            ## from data
            ET_event.image = utils.mock_image(event)
            ET_event.title = event['title']['fr']
            ET_event.public_transport = u'Non défini'
            ET_event.address = event['address']
            ET_event.contact = event['contributor']['organization']
            ET_event.price = event['conditions']['fr'] if event['conditions'] else 0
            ET_event.description = utils.set_event_description(event)

            ET_event.image_main = ET_event.image

            # delete previous versions of the same event
            try:
                previous_event = Event.objects.get(title=ET_event.title)
                Occurrence.objects.filter(event__pk=previous_event.id).delete()
                Event.objects.get(pk=previous_event.id).delete()
                updated_events.append(ET_event)

            except ObjectDoesNotExist:
                new_events.append(ET_event)


            # save event
            ET_event.save()

            # get and save occurrences
            ET_event.add_occurrences(*utils.get_occurrences(event))

        html = "<html><body>New events : %s. </br>"\
               "Updated events: %s </body></html>" \
               % (str([event.title for event in new_events]),
                  str([event.title for event in updated_events])
                  )

        return HttpResponse(html)
