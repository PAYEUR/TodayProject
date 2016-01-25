from django.db import models
from swingtime import models as md

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse


@python_2_unicode_compatible
class City(models.Model):
    """ City class. Use to make queries on city_name.
    """

    city_name = models.CharField(_('city_name'), max_length=30, default="Paris")

    def __str__(self):
        return self.city_name


@python_2_unicode_compatible
class EventWithImage(md.Event):
    """ Derives from swingtime. Event with one image related. Price, city and address
     also
    """

    image = models.ImageField(default=None)
    price = models.PositiveSmallIntegerField(default=0)
    city = models.ForeignKey(City)
    address = models.CharField(_('address'), max_length=150, default="non precise")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('get_event', kwargs={'event_id':self.pk})

@python_2_unicode_compatible
class EventTypeWithImage(md.EventType):
    """ Derives from swingtime. EventType with one image related
    """

    image = models.ImageField(default=None)

    def __str__(self):
        return self.label