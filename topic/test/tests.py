from django.test import TestCase, Client
# from django.core.urlresolvers import reverse

# TODO marche pas...
class ViewTests(TestCase):
    def SetUp(self):
        self.client = Client()

    def test_index(self):
        url = '/paris/spi'
        response = self.client.get(url)
        #self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'topic/research.html')
        self.assertContains(response, 'paris')
        self.assertContains(response, 'spi')
