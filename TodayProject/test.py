from django.test import TestCase, Client

from context_processors import *
from utils import *

from location.models import City
from topic.models import Topic

# context processor
class TestTopic_list(TestCase):
    def test_topic_list(self):
        self.fail()


class TestTopic_sidebar(TestCase):
    def test_topic_sidebar(self):
        self.fail()


class TestCities(TestCase):
    def test_cities(self):
        self.fail()

# utils
class TestGet_city_and_topic(TestCase):
    def SetUp(self):
        self.request = Client().get('/paris/spi/').request

    def test_get_city(self):
        self.assertEqual(get_city_and_topic(self.request)['city'], City.objects.get(city_name='paris'))

    def test_get_topic(self):
        self.assertEqual(get_city_and_topic(self.request)['topic'], City.objects.get(city_name='topic'))
