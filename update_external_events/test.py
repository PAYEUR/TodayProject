# coding = utf-8

from __future__ import print_function, unicode_literals
import json
import urllib2

from django.test import SimpleTestCase


class TestUtils(SimpleTestCase):

    def test_read_jsonfile(self):

        with open('update_external_events/events_paris.json', 'r') as json_f:
            data = json.load(json_f)
            self.assertEqual(data['total'], 387)

    def test_read_jsonurl(self):
        url = 'https://openagenda.com/agendas/82290100/events.json'
        response = urllib2.urlopen(url)
        self.assertEqual(response.getcode(), 200)
        try:
            json.load(response)
        except Exception:
            self.fail("json.load() raised an exeption")
