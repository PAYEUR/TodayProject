# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from datetime import datetime
import urllib2
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist

from topic.models import EventType, Topic


CORRESPONDING_EVENT_TYPE = {
    u'Retraite/pélerinage': [u'retraite', u'pelerinage'],
    u'Groupe de prière': [u'célébration', u'prière'],
    u'Réflexion et partage': [u'amitié', u'partage', u'réflexion'],
    u'Concert et spectacles': [u'concert', u'culture', u'exposition'],
    u'Action sociale': [u'action caritative', u'caritatifs', u'solidarité'],
    u'Adoration': [u'adoration', u'saint sacrement'],
    u'Confession': [u'pardon', u'confessions'],
    u'Conférence': [u'conférence', u'formation', u'enseignement', u'forum'],
    u'Autre': [],
}


def set_event_description(event):
    description = event['longDescription']['fr'] if event['longDescription'] else event['description']['fr']
    if event['registration']:
        description = "%s \n%s %s" % (description, u"Inscriptions:", event['registration'][0]['value'])
    return description


def get_occurrences(event):
    """
    :param event:
    :return: datetime_list, delta_hour (unique), isMultiple=True
    """
    datetime_list = []
    str_format = '%Y-%m-%dT%H:%M:%S.000Z'

    for timing in event['timings']:
        datetime_list.append(datetime.strptime(timing['start'], str_format))

    first_start = datetime.strptime(event['timings'][0]['start'], str_format)
    first_end = datetime.strptime(event['timings'][0]['end'], str_format)
    delta_hour = first_end - first_start

    return datetime_list, delta_hour, True


def get_image(event):
    """
    :param event:
    :return: SimpleUploadedFile fitting with ImageField
    """
    if event['image']:
        # download image locally
        image_url = urllib2.urlopen(event['image'])
        with open('update_external_events/last_event_image.jpg', 'w') as f:
            f.write(image_url.read())
        with open('update_external_events/last_event_image.jpg', 'rb') as f:
            return SimpleUploadedFile(f.name, f.read())
    else:
        with open('update_external_events/default.jpg', 'rb') as f:
            return SimpleUploadedFile(f.name, f.read())


def flush_image(image_name='last_event_image.jpg'):
    try:
        os.remove('update_external_events/%s' % image_name)
    except OSError:
        print("no %s in 'update_external_events' to remove" % image_name)
        pass


def get_event_type(event):
    """
    :param event
    :return:
    """
    event_type_list = []
    for tag in event['tags']:
        for k, v_list in CORRESPONDING_EVENT_TYPE.items():
            for v in v_list:
                for word in tag['label'].lower().split(' '):
                    if word in v:
                        try:
                            event_type_list.append(EventType.objects.get(label=k))
                        except ObjectDoesNotExist:
                            print('event_type of CORRESPONDING_EVENT_TYPE not in database')
    if event_type_list:
        return event_type_list[0]  # if different event_type possible, returns the first
    else:
        topic = Topic.objects.get(name='spi')
        return EventType.objects.filter(label=u'Autre').filter(topic=topic)[0]


# TODO: convert this to openstreet map or google maps
def get_address(event):
    """
    :param event:
    :return: full ET address
    """
    address = event['location']['address']
    name = event['location']['name']
    return u'%s, %s' % (name, address)
