from django.test import TestCase
import context_processors
from django.contrib.auth.models import User

# see https://docs.djangoproject.com/fr/1.11/topics/testing/tools/


# utils
class TestContextProcessors(TestCase):

    def test_topic_list(self):
        self.assertIsInstance(context_processors.topic_list, object)

    def test_cities_list(self):
        self.assertIsInstance(context_processors.cities_list, object)


# urls
class TestAdminUrl(TestCase):

    def test_without_login(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_with_non_superuser_login(self):
        user = User.objects.create_user(username='foo', email='test@test.com', password='bar')
        self.client.force_login(user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_with_superuser_login(self):
        user = User.objects.create_superuser(username='foo', email='test@test.com', password='bar')
        self.client.force_login(user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


# other urls tested in subapplications
