# coding = utf-8

from __future__ import print_function, unicode_literals
import json
import urllib2

from django.test import SimpleTestCase


class TestUtils(SimpleTestCase):

    def test_read_jsonfile(self):

        with open('update_external_events/events_paris.json', 'r') as json_f:
            print(json_f.read()[:10])
            data = json.loads(json_f.read(), 'utf-8')
            print(data)
            self.assertEqual(data['total'], 307)

    def test_read_jsonurl(self):
        url = 'https://openagenda.com/agendas/82290100/events.json'
        data = json.load(urllib2.urlopen(url))
        print(data['total'])
