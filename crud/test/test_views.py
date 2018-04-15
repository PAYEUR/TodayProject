# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)
from datetime import date, timedelta, time

from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse

from topic.models import Topic, EventType, Event
from location.models import City

FIXTURES = ['fixtures/data_test.json']


class AddEventTest(TestCase):

    fixtures = FIXTURES

    def setUp(self):

        self.client.login(username='machin', password='machinchose')

        # Event_data
        self.event_data = {
            # using SimpleUploadedFile for image field
            'title': "Random title hrgjzefaj",
            'description': "Description",
            'price': '4683',
            'contact': "Ceci est un contact",
            'address': "Ceci est une adresse",
            'public_transport': "Ceci est un métro",
            'location': City.objects.get(city_slug="paris").pk,
            }

        # EventTypeByTopic data
        self.topic1 = Topic.objects.get(name='spi')
        self.event_type1 = EventType.objects.get(label='Confession')
        self.key1 = str(self.topic1.name) + "-event_type"

        self.event_type_by_topic_data = {self.key1: self.event_type1.pk}

        # EventTypeByTopic data
        self.single_formset_data = {
            'single_occurrence-TOTAL_FORMS': '10',
            'single_occurrence-INITIAL_FORMS': '1',
            'single_occurrence-MIN_NUM_FORMS': '1',
            'single_occurrence-0-start_date': date.today() + timedelta(days=1),
            'single_occurrence-0-end_date': date.today() + timedelta(days=2),
            'single_occurrence-0-start_time': time(hour=14, minute=25),
            'single_occurrence-0-end_time': time(hour=15, minute=25),
            }

        self.multi_formset_data = {
            'multiple_occurrence-TOTAL_FORMS': '1',
            'multiple_occurrence-INITIAL_FORMS': '1',
            'multiple_occurrence-MIN_NUM_FORMS': '1',
            'multiple_occurrence-0-start_date': date.today() + timedelta(days=1),
            'multiple_occurrence-0-end_date': date.today() + timedelta(days=2),
            'multiple_occurrence-0-start_time': time(hour=8, minute=25),
            'multiple_occurrence-0-end_time': time(hour=9, minute=25),
            'multiple_occurrence-0-week_days': [1, 2]
            }

        self.multi_formset_empty_data = {
            'multiple_occurrence-TOTAL_FORMS': '1',
            'multiple_occurrence-INITIAL_FORMS': '1',
            'multiple_occurrence-MIN_NUM_FORMS': '1',
            }

        # all data included
        super_dict = {}
        for d in [self.event_data,
                  self.event_type_by_topic_data,
                  self.single_formset_data,
                  self.multi_formset_empty_data]:
            for k, v in d.iteritems():
                super_dict.setdefault(k, []).append(v)
        self.data = super_dict

        # multi invalid data
        super_dict = {}
        for d in [self.event_data,
                  self.event_type_by_topic_data,
                  self.single_formset_data,
                  self.multi_formset_data]:
            for k, v in d.iteritems():
                super_dict.setdefault(k, []).append(v)
        self.multi_invalid_data = super_dict

    def test_valid_data(self):

        with open("crud/test/adoration.jpg", 'rb') as image:

            response = self.client.post(reverse('crud:create_event'),
                                        dict(self.data, **{'image': image}),
                                        )

            # raise Http404 error if event not saved
            get_object_or_404(Event, title="Random title hrgjzefaj")

            self.assertRedirects(response, reverse('crud:event_planner_panel'))

    def test_invalid_occurrence_data(self):
        data = self.data.copy()
        data['single_occurrence-0-start_date'] = date.today() + timedelta(days=5)
        with open("crud/test/adoration.jpg", 'rb') as image:
            self.client.post(reverse('crud:create_event'),
                             dict(data, **{'image': image}),
                             )

            with self.assertRaisesMessage(Http404, 'No Event matches the given query.'):
                get_object_or_404(Event, title="Random title hrgjzefaj")

    def test_invalid_event_data(self):
        data = self.data.copy()
        data['description'] = ''
        with open("crud/test/adoration.jpg", 'rb') as image:
            self.client.post(reverse('crud:create_event'),
                             dict(data, **{'image': image}),
                             )

            with self.assertRaisesMessage(Http404, 'No Event matches the given query.'):
                get_object_or_404(Event, title="Random title hrgjzefaj")

    def test_multi_occurrences_data(self):
        with open("crud/test/adoration.jpg", 'rb') as image:
            response = self.client.post(reverse('crud:create_event'),
                                         dict(self.multi_invalid_data, **{'image': image}),
                                         )

            self.assertEquals(response.context['occurrence_error'], True)

    def test_multi_event_type_by_topic_form_data(self):
        """
        Test two filled event_type_by_topic_form.
        Must raise topic_error = True
        :return:
        """
        topic2 = Topic.objects.get(name='jobs')
        event_type2 = EventType.objects.get(label='Jardinage')
        key2 = str(topic2.name) + "-event_type"

        event_type_by_topic_data_2 = {key2: event_type2.pk}
        data = dict(self.data, **event_type_by_topic_data_2)
        with open("crud/test/adoration.jpg", 'rb') as image:
            response = self.client.post(reverse('crud:create_event'),
                                        dict(data, **{'image': image}),
                                        )

            self.assertEquals(response.context['topic_error'], True)

    def test_valid_data_logout(self):
        self.client.logout()

        with open("crud/test/adoration.jpg", 'rb') as image:

            response = self.client.post(reverse('crud:create_event'),
                                        dict(self.data, **{'image': image}),
                                        )

            self.assertRedirects(response, '/connexion/login?next=/nouvel_evenement')


class EventPlannerPanelViewTest(TestCase):

    fixtures = FIXTURES

    def setUp(self):
        self.client.login(username='machin', password='machinchose')
        self.event1 = Event.objects.get(title="AdorationAlbi Test")
        self.event2 = Event.objects.get(title="ConferenceTest")
        self.response = self.client.get(reverse('crud:event_planner_panel'))

    def test_is_logged(self):
        """
        :return: redirects to 'crud:event_planner' if user is logged
        """
        self.assertEquals(self.response.status_code, 200)

    def test_is_not_logged(self):
        """
        :return: redirects to 'connection:login' if user is not logged
        """
        self.client.logout()
        self.response = self.client.get(reverse('crud:event_planner_panel'))
        self.assertRedirects(self.response, '/connexion/login?next=/tableau-de-bord')

    def test_context(self):
        context = self.response.context
        assert self.event1, self.event2 in context['events']

    def test_template(self):
        # test with events
        self.assertNotContains(self.response, "Pas d'événements programmés")

        # tests with no events
        self.client.login(username='tata', password='thisisanotherpassword')
        response = self.client.get(reverse('crud:event_planner_panel'))
        self.assertContains(response, "Pas d'événements programmés")



