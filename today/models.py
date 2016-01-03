from __future__ import unicode_literals

from django.db import models
from swingtime.models import Event


class Image(models.Model):
    """ Single table that contains images either from download from existing db
    """
    field = models.ImageField()


class EventWithImage(models.Model):
    """ swingtime.Event + Image so that an event in todayProject is necessarily linked to an image
    """
    event = models.ForeignKey(Event)
    image = models.ForeignKey(Image)

    def __str__(self):
        return self.title
