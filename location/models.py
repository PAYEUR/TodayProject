from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# here gonna be also site configuration, as there is one website for each different city.


# ==============================================================================
@python_2_unicode_compatible
class City(models.Model):
    """ Place class. Use to make queries on city.
    """

    city_name = models.CharField(verbose_name='city_name',
                                 max_length=255,
                                 default="Paris")
    #location = PlainLocationField(based_fields=['city_name'], zoom=7, default="Null")

    # ==========================================================================
    class Meta:
        verbose_name ='city'
        verbose_name_plural ='cities'

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.city_name


# other stuff
# @python_2_unicode_compatible
# class Adress()
    # gonna put google location api somewhere here