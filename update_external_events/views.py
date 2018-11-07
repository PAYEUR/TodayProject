# coding = utf-8

import json

from django.http import HttpResponse

from topic.models import Event, EventType
from location.models import City


def update_external_events(request):

    # 1) reformat json file to make sure its encoding is utf-8
    # TODO

    # 2) read data
    with open('update_external_events/events_paris.json', 'r') as json_f:
        data = json.load(json_f)
        html = "<html><body>data['readme'] : %s.</body></html>" % data['readme']
        return HttpResponse(html)

