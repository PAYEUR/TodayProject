from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# ==============================================================================
@python_2_unicode_compatible
class EnjoyTodayUser(models.Model):

    user = models.ForeignKey(User,
                             default=None,
                             null=True,
                             on_delete=models.SET_DEFAULT)

    # other attributes if needed

    class Meta:
        verbose_name = 'EnjoyToday user'
        verbose_name_plural ='EnjoyToday users'

    def __str__(self):
        return "{0} posts in EnjoyToday".format(self.user.username)

    # def get_absolute_url(self):
        # return reverse('core:event_planner_panel')
