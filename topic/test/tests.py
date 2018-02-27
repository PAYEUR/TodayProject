from django.test import TestCase
from datetime import datetime, timedelta, time
from topic import utils, views
from topic.models import EventType, Topic, Event, Occurrence
from location.models import City


# utils
class TestUtils(TestCase):

    start_time = datetime(day=1, month=1, year=2001, hour=1, minute=1)
    end_time = datetime(day=2, month=2, year=2002, hour=2, minute=2)

    def setUp(self):
        Topic.objects.create(name='spi')
        Topic.objects.create(name='job')
        self.topic1 = Topic.objects.get(name='spi')
        self.topic2 = Topic.objects.get(name='job')
        EventType.objects.create(topic=self.topic1, label='event_type1', image=None)
        EventType.objects.create(topic=self.topic1, label='event_type2', image=None)
        EventType.objects.create(topic=self.topic2, label='event_type3', image=None)

    def test_construct_hour(self):
        hour_string = '2h06'
        answer = time(hour=2, minute=6)
        self.assertEqual(utils.construct_hour(hour_string), answer)

    def test_construct_hour_string(self):
        datetime_hour = time(hour=1, minute=1)
        self.assertEqual(utils.construct_hour_string(datetime_hour), '01h01')

    def test_create_date_url_dict(self):
        date_url_dict = utils.create_date_url_dict(self.start_time, self.end_time)
        self.assertEqual(date_url_dict['start_date'], '1')

    def test_create_id_string(self):
        object_list = EventType.objects.filter(topic=self.topic1)
        self.assertEqual(utils.create_id_string(object_list), '1&2')

    def test_event_type_list1(self):
        event_type_id_string = '1'
        event_type_list = utils.get_event_type_list(event_type_id_string)
        label = event_type_list[0].label
        self.assertEqual(label, 'event_type1')

    def test_event_type_list2(self):
        event_type_id_string = '1&2'
        event_type_list = utils.get_event_type_list(event_type_id_string)
        label = event_type_list[1].label
        self.assertEqual(label, 'event_type2')

    def test_url_all_events_dict1(self):
        event_type_id_string = utils.url_all_events_dict(self.topic1,
                                                         self.start_time,
                                                         self.end_time)['event_type_id_string']
        self.assertEqual(event_type_id_string, '1&2')

    def test_url_all_events_dict2(self):
        event_type_id_string = utils.url_all_events_dict(self.topic2,
                                                         self.start_time,
                                                         self.end_time)['event_type_id_string']
        self.assertEqual(event_type_id_string, '3')


# url
class TestUrl(TestCase):

    fixtures = ['data_test.json']

    def test_full_list_url(self):
        url = '/paris/spi/categorie1/du_21-05-2017_a_12h00/au_21-05-2017_a_13h00'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

