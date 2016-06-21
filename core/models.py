# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse

@python_2_unicode_compatible
class Topic(models.Model):
    """
    topic class, for example "catho" or "jobs"
    """
    name = models.CharField(verbose_name="Thématique",
                            max_length=50,
                            default=None)

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.name

    # --------------------------------------------------------------------------
    #def get_absolute_url(self):
        #return reverse('topic:index')
