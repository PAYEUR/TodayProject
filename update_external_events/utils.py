# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import sys
from datetime import datetime, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile


def convert_to_utf8(filename):
    # gather the encodings you think that the file may be
    # encoded inside a tuple
    encodings = ('windows-1253', 'iso-8859-7', 'utf-8')

    with open(filename, 'r') as f:
        for enc in encodings:
            try:
                data = f.read().decode(enc)
                break
            except UnicodeDecodeError:
                if enc == encodings[-1]:
                    print('Encoding doesn\'t belong to' + ' ,'.join(encodings))
                    sys.exit(1)
                continue

    # and at last convert it to utf-8
    with open(filename, 'w') as f:
        f.write(data.encode('utf-8'))


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
    format = '%Y-%m-%dT%H:%M:%S.000Z'

    for timing in event['timings']:
        datetime_list.append(datetime.strptime(timing['start'], format))

    first_start = datetime.strptime(event['timings'][0]['start'], format)
    first_end = datetime.strptime(event['timings'][0]['end'], format)
    delta_hour = first_end - first_start

    return datetime_list, delta_hour, True


def mock_image(event):
    """
    Mock an uploaded image and set the url (which is the only accessed attribute)
    :param event:
    :return:
    """
    upload_file = open("update_external_events/mock.jpg", 'rb')
    image = SimpleUploadedFile(upload_file.name, upload_file.read())
    image.url = event['image']
    return image
