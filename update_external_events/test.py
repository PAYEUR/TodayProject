# coding = utf-8

from __future__ import print_function, unicode_literals
import json
import urllib2

from django.test import SimpleTestCase


class TestData(SimpleTestCase):

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


class TestUrlForUpdate(SimpleTestCase):

    def test_url(self):
        url = '/paris/test-update'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
