# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from django.test import TestCase
from crud.forms import EventForm
from topic.models import Event
from location.models import City
from django.core.files.images import ImageFile
import mock


class EventFormTests(TestCase):

    def test_valid(self):

        data = {
            'image': mock.MagicMock(spec=ImageFile, name='ImageMock'),
            'title': "Titre",
            'description': "Description",
            'price': 1,
            'contact': "Ceci est un contact",
            'address': "Ceci est une adresse",
            'public_transport': "Ceci est un métro",
            'location': City.objects.get(city_slug="paris"),
        }


