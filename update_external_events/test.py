# coding = utf-8

from __future__ import print_function, unicode_literals
import json
import urllib2
from datetime import datetime, timedelta

from django.test import SimpleTestCase

import utils


class TestRawData(SimpleTestCase):

    def test_jsonfile(self):

        with open('update_external_events/events_paris.json', 'r') as json_f:
            data = json.load(json_f)
            self.assertEqual(data['total'], 387)

    # def test_jsonurl(self):
    #     url = 'https://openagenda.com/agendas/82290100/events.json'
    #     response = urllib2.urlopen(url)
    #     self.assertEqual(response.getcode(), 200)
    #     try:
    #         json.load(response)
    #     except Exception:
    #         self.fail("json.load() raised an exeption")


class TestUrlForUpdate(SimpleTestCase):

    def test_url(self):
        url = '/paris/test-update'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestUtils(SimpleTestCase):

    def setUp(self):
        with open('update_external_events/events_paris.json', 'r') as json_f:
            self.data = json.load(json_f)
            self.event = self.data['events'][0]

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
