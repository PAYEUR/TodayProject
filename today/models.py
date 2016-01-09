from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from swingtime.models import Event


@python_2_unicode_compatible
class Picture(models.Model):
    """ Single table that contains images either from download or from existing db
        Each Image is related to one single Event
    """
    image = models.ImageField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.event.title
