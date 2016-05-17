from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User

# ==============================================================================
@python_2_unicode_compatible
class EventPlanner(models.Model):
    user = models.OneToOneField(User)
    #other attributes if needed

    class Meta:
        verbose_name = 'event planner'
        verbose_name_plural ='event planners'

    def __str__(self):
        return "user {0} as event planner".format(self.user.username)

     #def get_absolute_url(self):
        #return reverse('event_planner_panel', kwargs={'event_planner_id': self.pk})