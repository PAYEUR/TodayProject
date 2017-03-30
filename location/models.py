# coding=utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
#from topic.models import Topic

# rewrite this to properly take into account site and related cities

# ==============================================================================
@python_2_unicode_compatible
class City(models.Model):
    """ Place class. Use to make queries on city.
    """

    city_name = models.CharField(verbose_name='city_name',
                                 default="Paris",
                                 max_length=255,
                                 help_text="Nom de la ville")

    city_slug = models.CharField(verbose_name='city_slug',
                                 default='paris',
                                 max_length=255,
                                 help_text="Nom de la ville affiché dans l'url")

    city_big_map_coordinates = models.CharField(verbose_name='city_big_map_coordinates',
                                                default="155,52,155,83,238,88,237,56",
                                                max_length=255,
                                                help_text="Coordonnées html de la zone de la grande carte de France "
                                                          "correspondant à la ville, au format 155,52,155,83,238,88,237,56")

    city_small_map_coordinates = models.CharField(verbose_name='city_small_map_coordinates',
                                                  default="89,33,88,48,136,49,135,37",
                                                  max_length=255,
                                                  help_text="Coordonnées html de la zone de la petite carte de France "
                                                            "correspondant à la ville, au format 155,52,155,83,238,88,237,56")

    # TODO: automatize topic_name
    def get_absolute_url(self):
        """
        by default, returns catho index page
        """
        return reverse('topic:index',
                       kwargs={'city_slug': self.city_slug,
                               'topic_name': 'catho',
                               # 'topic_name': Topic.Field('name').default,
                               }
                       )

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