# coding = utf-8

import json

from topic.models import Event, EventType
from location.models import City


def update_external_events(request):

    # 1) reformat json file to make sure its encoding is utf-8
    # TODO

    # 2) read data
    with open('events_paris.json', 'r') as json_f:
        data = json.load(json_f)
        print(data['readme'])

