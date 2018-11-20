# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import json
import urllib2
from datetime import datetime, timedelta
from unittest import skip

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from topic.models import EventType
import utils

FIXTURES = ['fixtures/data_test.json']


class TestRawData(TestCase):

    def test_jsonfile(self):

        with open('update_external_events/events_paris.json', 'r') as json_f:
            data = json.load(json_f)
            self.assertEqual(data['total'], 387)

    def test_jsonurl(self):
        url = 'https://openagenda.com/agendas/82290100/events.json'
        response = urllib2.urlopen(url)
        self.assertEqual(response.getcode(), 200)
        try:
            json.load(response)
        except Exception:
            self.fail("json.load() raised an exeption")


class TestUrlForUpdate(TestCase):

    fixtures = FIXTURES

    def test_url(self):
        url = '/paris/test-update'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestUtils(TestCase):

    fixtures = FIXTURES

    def setUp(self):
        with open('update_external_events/events_paris.json', 'rb') as json_f:
            self.data = json.load(json_f)
            self.event = self.data['events'][0]

    def tearDown(self):
        utils.flush_image()

    def test_set_event_description_with_registration(self):
        description = utils.set_event_description(self.event)
        self.assertGreater(len(description), len(self.event['longDescription']))
        self.assertTrue("Inscriptions" in description)

    def test_set_event_description_without_registration(self):
        self.event['registration'] = []
        description = utils.set_event_description(self.event)
        self.assertEqual(description, self.event['longDescription']['fr'])

    def test_get_occurrences(self):
        datetime_list, delta_hour, is_multiple = utils.get_occurrences(self.event)

        self.assertEqual(datetime_list[0],
                         datetime.strptime('2018-11-06T19:30:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
                         )
        self.assertEqual(delta_hour, timedelta(hours=1))

    def test_get_image_for_existing_image(self):
        image = utils.get_image(self.event)
        with open('update_external_events/last_event_image.jpg', 'rb') as f:
            upload_file = SimpleUploadedFile(f.name, f.read())
            self.assertEqual(image.read(), upload_file.read())

    def test_get_image_by_default(self):
        self.event['image'] = ''
        image = utils.get_image(self.event)
        with open('update_external_events/default.jpg', 'rb') as f:
            upload_file = SimpleUploadedFile(f.name, f.read())
            self.assertEqual(image.read(), upload_file.read())

    def test_get_event_type_not_in_db(self):
        """
        event_type not in DB
        :return: EventType.Objects.get(label=u'Autre')
        """
        self.assertEqual(utils.get_event_type(self.event), EventType.objects.get(label=u'Autre'))

    def test_get_event_type_in_db(self):
        """
        event_type in DB
        :return: EventType.Objects.get(label=u'Conférence')
        """
        self.event = self.data['events'][10]
        self.assertEqual(utils.get_event_type(self.event), EventType.objects.get(label=u'Conférence'))

    def test_get_address(self):
        address = utils.get_address(self.event)
        self.assertEqual(address, u'Cathédrale Notre-Dame de Paris, 6 parvis Notre-Dame, 75004 Paris')


