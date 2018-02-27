# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.test import TestCase
from django import forms
from crud.forms import (EventForm,
                        EventTypeByTopicForm,
                        SingleOccurrenceForm,
                        MultipleOccurrenceForm,
                        FormsListManager,
                        )
from topic.models import Topic, EventType, EnjoyTodayUser, Event, Occurrence
from location.models import City
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta, time


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

        self.data = {
            'single_occurrence-start_date': date.today() + timedelta(days=1),
            'single_occurrence-end_date': date.today() + timedelta(days=2),
            'single_occurrence-start_time': time(hour=14, minute=25),
            'single_occurrence-end_time': time(hour=15, minute=25),
        }

    def test_valid_data(self):
        form = SingleOccurrenceForm(self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_date(self):
        """
        :return: check that start_time < now raises a ValidationError
        """
        data = self.data.copy()
        data['single_occurrence-end_date'] = data['single_occurrence-start_date'] - timedelta(days=5)
        form = SingleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_invalid_time(self):
        """
        :return: check that start_time > end_time raises a ValidationError
        """
        data = self.data.copy()
        data['single_occurrence-start_date'] += timedelta(days=5)
        form = SingleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_save(self):
        form = SingleOccurrenceForm(self.data)
        event = Event.objects.get(title="ConferenceTest")

        if form.is_valid():
            form.save(event)

        occurrence = Occurrence.objects.get(start_time=form.start_datetime,
                                            end_time=form.end_datetime)
        self.assertEqual(occurrence.event, event)


class MultipleOccurrenceFormTest(TestCase):

    fixtures = ['data_test.json']

    def setUp(self):

        self.data = {
            'multiple_occurrence-start_date': date.today() + timedelta(days=1),
            'multiple_occurrence-end_date': date.today() + timedelta(days=2),
            'multiple_occurrence-start_time': time(hour=8, minute=25),
            'multiple_occurrence-end_time': time(hour=9, minute=25),
            'multiple_occurrence-week_days': [1, 2]
        }

    def test_valid_data(self):
        form = MultipleOccurrenceForm(self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_date(self):
        """
        :return: check that start_time < now raises a ValidationError
        """
        data = self.data.copy()
        data['multiple_occurrence-end_date'] = data['multiple_occurrence-start_date'] - timedelta(days=5)
        form = MultipleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_invalid_time(self):
        """
        :return: check that start_time > end_time raises a ValidationError
        """
        data = self.data.copy()
        data['multiple_occurrence-start_date'] += timedelta(days=5)
        form = MultipleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('__all__' in form.errors.as_data().keys())

    def test_invalid_week_days(self):
        data = self.data.copy()
        data['multiple_occurrence-week_days'] = [18]
        form = MultipleOccurrenceForm(data)
        self.assertFalse(form.is_valid())
        data['multiple_occurrence-week_days'] = ['foo']
        form = MultipleOccurrenceForm(data)
        self.assertFalse(form.is_valid())

    def test_save(self):
        form = MultipleOccurrenceForm(self.data)
        event = Event.objects.get(title="ConferenceTest")

        if form.is_valid():
            form.save(event)

        occurrence = Occurrence.objects.get(start_time=form.start_datetime,
                                            end_time=form.end_datetime)
        self.assertEqual(occurrence.event, event)


class MockForm(forms.Form):

    mock_field = forms.CharField()


class FormListManagerTest(TestCase):

    def setUp(self):
        mock_data = {'mock_field': "foo"}
        filled_mock_formset_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '1',
            'form-0-mock_field': "foo"
            }
        blank_mock_formset_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '1',
            }
        MockFormSet = forms.formset_factory(MockForm, min_num=1, validate_min=True)
        self.filled_form = MockForm(mock_data)
        self.filled_formset = MockFormSet(filled_mock_formset_data)
        self.blank_form = MockForm()
        self.blank_formset = MockFormSet(blank_mock_formset_data)

    def test_check_two_filled_forms(self):
        # 1 filled formset and 1 filled form
        form_list_manager = FormsListManager()
        forms_test_list = [self.filled_form, self.filled_formset]
        form_list_manager.check_filled_forms(forms_test_list)
        self.assertEqual(form_list_manager.filled_forms, forms_test_list)

    def test_check_one_filled_forms(self):
        # 1 filled formset and 1 blank form
        form_list_manager = FormsListManager()
        form_list_manager.check_filled_forms([self.blank_form, self.filled_formset])
        self.assertEqual(form_list_manager.filled_forms, [self.filled_formset])

    def test_check_zero_filled_forms(self):
        # 1 blank formset and 1 blank form
        form_list_manager = FormsListManager()
        form_list_manager.check_filled_forms([self.blank_form, self.blank_formset])
        self.assertEqual(form_list_manager.filled_forms, [])

    def test_only_one_form_is_filled1(self):
        form_list_manager = FormsListManager()
        form_list_manager.check_filled_forms([self.blank_formset, self.filled_formset])
        self.assertTrue(form_list_manager.only_one_form_is_filled())

    def test_only_one_form_is_filled2(self):
        form_list_manager = FormsListManager()
        form_list_manager.check_filled_forms([self.filled_formset, self.filled_form])
        self.assertFalse(form_list_manager.only_one_form_is_filled())

# integration test with 3 forms

# then switch to view test...