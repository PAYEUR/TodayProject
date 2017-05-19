from django.test import TestCase, Client
import utils

from location.models import City
from topic.models import Topic


# utils
class TestContextProcessors(TestCase):

    def test_topic_list(self):
        self.assertIsInstance(list)

    def test_cities_list(self):
        self.assertIsInstance(list)