from django.test import TestCase, Client
import utils

from location.models import City
from topic.models import Topic


# utils
class TestUtils(TestCase):
    def SetUp(self):
        self.request = Client().get('/paris/spi/').request

    def test_get_city(self):
        self.assertEqual(utils.get_city_and_topic(self.request)['city'], City.objects.get(city_name='paris'))

    def test_get_topic(self):
        self.assertEqual(utils.get_city_and_topic(self.request)['topic'], Topic.objects.get(city_name='spi'))
