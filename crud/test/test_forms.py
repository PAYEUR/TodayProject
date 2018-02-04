# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.test import TestCase
from crud.forms import EventForm, EventTypeByTopicForm
from topic.models import Topic, EventType, EnjoyTodayUser, Event
from location.models import City
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
import os


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
        self.data1 = {'event_type': self.event_type1.pk}
        self.data2 = {'event_type': self.event_type1.pk}

    def test_good_input_data(self):
        self.assertEqual(self.topic1, self.event_type1.topic)
        self.assertEqual(self.topic2, self.event_type2.topic)

    # TODO: finish this
    def test_valid_data1(self):
        form = EventTypeByTopicForm(self.data1, topic=self.topic1)
        print(form)
        # the form is correctly constructed
        #self.assertTrue(form.is_bound)
        #elf.assertTrue(form.is_valid())

    def test_valid_data2(self):
        form = EventTypeByTopicForm(self.data2, topic=self.topic2)
        print(form)

    def test_blank_data(self):
        form = EventTypeByTopicForm(self.topic, {})
        self.assertFalse(form.is_valid())
        print(form.errors)

