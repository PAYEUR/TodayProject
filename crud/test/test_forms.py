# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.test import TestCase
from crud.forms import EventForm, EventTypeByTopicForm, SingleOccurrenceForm
from topic.models import Topic, EventType, EnjoyTodayUser, Event, Occurrence
from location.models import City
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, date, timedelta, time


# from http://test-driven-django-development.readthedocs.io/en/latest/05-forms.html
# https://docs.djangoproject.com/fr/1.11/topics/testing/tools/
# testing file upload:
class EventFormTest(TestCase):

    fixtures = ['data_test.json']

    def setUp(self):
        self.data = {
            # using SimpleUploadedFile for image field
            'title': "Titre",
            'description': "Description",
            'price': '1',
            'contact': "Ceci est un contact",
            'address': "Ceci est une adresse",
            'public_transport': "Ceci est un métro",
            'location': City.objects.get(city_slug="paris").pk,
            }

        # https://stackoverflow.com/questions/2473392/unit-testing-a-django-form-with-a-filefield
        upload_file = open("crud/test/adoration.jpg", 'rb')
        self.file_data = {'image': SimpleUploadedFile(upload_file.name,
                                                      upload_file.read())}

    def test_valid_data(self):
        form = EventForm(self.data, self.file_data)
        print(form.errors)
        # print(self.file_data)
        # print(City.objects.get(city_slug="paris"))
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = EventForm({}, self.file_data)
        self.assertFalse(form.is_valid())

    def test_save(self):
        form = EventForm(self.data, self.file_data)

        # create event object and save it
        event = form.save(commit=False)
        event.event_type = EventType.objects.get(label='Confession')
        event.event_planner = EnjoyTodayUser.objects.get(user__username='machin')
        # print(event.event_type)
        # print(event.event_planner)
        event.save()

        # get the saved event object
        event2 = Event.objects.get(title="Titre")

        self.assertEqual(event, event2)


class EventTypeByTopicFormTest(TestCase):

    fixtures = ['data_test.json']

    def setUp(self):
        self.topic1 = Topic.objects.get(name='spi')
        self.topic2 = Topic.objects.get(name='jobs')
        self.event_type1 = EventType.objects.get(label='Confession')
        self.event_type2 = EventType.objects.get(label='jardinage')
        # pay attention to the prefix attribute within the form
        self.key1 = str(self.topic1.name) + "-event_type"
        self.data = {self.key1: self.event_type1.pk}

    def test_good_input_data(self):
        self.assertEqual(self.topic1, self.event_type1.topic)
        self.assertEqual(self.topic2, self.event_type2.topic)

    def test_valid_data_with_prefix(self):
        form = EventTypeByTopicForm(self.data, topic=self.topic1)
        # need to call is_valid method in order to create form.cleaned_data attribute
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['event_type'], self.event_type1)

    # depends on required parameter in event_type field
    def test_blank_data(self):
        form = EventTypeByTopicForm({}, topic=self.topic1)
        # print(form)
        self.assertFalse(form.is_valid())


class SingleOccurrenceFormTest(TestCase):

    fixtures = ['data_test.json']

    def setUp(self):
        self.start_time = time(hour=14, minute=25)
        self.end_time = time(hour=15, minute=25)

        self.data = {
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today() + timedelta(days=2),
            'start_time': self.start_time,
            'end_time': self.end_time,
        }

    def test_valid_data(self):
        form = SingleOccurrenceForm(self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_date(self):
        """
        :return: check that start_time < now raises a ValidationError
        """
        data = self.data.copy()
        data['end_date'] = data['start_date'] - timedelta(days=5)
        form = SingleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_invalid_time(self):
        """
        :return: check that start_time > end_time raises a ValidationError
        """
        data = self.data.copy()
        data['start_date'] += timedelta(days=5)
        form = SingleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_save(self):
        form = SingleOccurrenceForm(self.data)
        event = Event.objects.get(title="ConferenceTest")
        # event.title = "Title"
        # event.image = None
        # event.description = "this is a description"
        # event.event_type = EventType.objects.get(label='ConferenceTest')
        # event.price = 18
        # event.contact = "foo"
        # event.address = "7, rue perronnet 75007 Paris"
        # event.public_transport = "this is a bus"
        # event.location = City.objects.get(city_slug="paris")
        # event.event_planner = EnjoyTodayUser.objects.get(user__username='machin')
        # event.created_at = datetime.today()
        # event.image_main = None

        if form.is_valid():
            saved_event = form.save(event)

        occurrence = Occurrence.objects.get(start_time=self.start_time,
                                            end_time=self.end_time)
        self.assertEqual(occurrence.event, event)


#class MultipleOccurrenceFormTest(TestCase):

#class FormListManagerTest(TestCase):

# integration test with 3 forms

# then switch to view test...