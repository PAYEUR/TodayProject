# coding=utf-8

from datetime import datetime
from dateutil import rrule
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.db import models
from django.core.urlresolvers import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from connection.models import EnjoyTodayUser
from location.models import City
from core.models import Topic


__all__ = (
    'EventType',
    'Event',
    'Occurrence',
)


# ==============================================================================
@python_2_unicode_compatible
class EventType(models.Model):
    """
    Simple ``Event`` classification.
    """
    topic = models.ForeignKey(Topic,
                              verbose_name='Thematique',
                              default=None)

    label = models.CharField(verbose_name='label', max_length=50)
    image = models.ImageField(default=None, upload_to='event_types/')
    #image_main = ImageSpecField(source='image',
                                #processors=[ResizeToFit(450, 300)],
                                #format='JPEG',
                                #options={'quality': 100})

    # ==========================================================================
    class Meta:
        verbose_name = 'event type'
        verbose_name_plural = 'event types'

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('topic:event_type_coming_days', kwargs={'event_type_id': self.pk})

# ==============================================================================
@python_2_unicode_compatible
class Event(models.Model):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    title = models.CharField(verbose_name="Titre",
                             max_length=100)

    description = models.TextField(verbose_name="Description")

    event_type = models.ForeignKey(EventType,
                                   verbose_name="Catégorie")


    image = models.ImageField(verbose_name="Image",
                              default=None,
                              upload_to='events/')

    price = models.PositiveSmallIntegerField(verbose_name="Prix en euros",
                                             default=0)

    image_main = ImageSpecField(source='image',
                                processors=[ResizeToFill(800, 300)],
                                format='JPEG',
                                options={'quality': 100})

    event_planner = models.OneToOneField(EnjoyTodayUser,
                                        default=None,
                                        null=True,
                                        blank=True,
                                        #editable=False,
                                        verbose_name='annonceur',
                                        )

    #Will remove this and use google place API instead
    city = models.ForeignKey(City,
                             verbose_name="Ville",
                             default={'city_name': "Paris"})

    address = models.CharField(verbose_name="Adresse",
                               max_length=150,
                               default="non précisé")

    # ===========================================================================
    class Meta:
        verbose_name = 'event'
        verbose_name_plural = 'events'
        ordering = ('title', )

    # ---------------------------------------------------------------------------
    def __str__(self):
        return self.title

    # --------------------------------------------------------------------------
    #def get_absolute_url(self):
        #return reverse('', kwargs={'event_id': self.pk})

    def delete_url(self):
        return reverse('topic:crud:delete_event', kwargs={'event_id': self.pk})

    def update_url(self):
        return reverse('topic:crud:update_event', kwargs={'event_id': self.pk})


    # --------------------------------------------------------------------------
    def add_occurrences(self, start_time, end_time, is_multiple, **rrule_params):
        """
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If ``until`` entry is missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        """

        until = rrule_params.get('until')
        if not until:
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            delta_hour = end_time - start_time
            occurrences = []
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(Occurrence(start_time=ev,
                                              end_time=ev + delta_hour,
                                              event=self,
                                              is_multiple=is_multiple))
            self.occurrence_set.bulk_create(occurrences)

    # --------------------------------------------------------------------------
    def upcoming_occurrences(self):
        """
        Return all occurrences that are set to start on or after the current
        time.
        """
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    # --------------------------------------------------------------------------
    def next_occurrence(self):
        """
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        """
        upcoming = self.upcoming_occurrences()
        return upcoming[0] if upcoming else None

    # --------------------------------------------------------------------------
    def daily_occurrences(self, dt=None):
        """
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        """
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)


# ==============================================================================
class OccurrenceManager(models.Manager):

    use_for_related_fields = True

    # --------------------------------------------------------------------------
    def daily_occurrences(self, dt=None, event=None):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        """
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )

        return qs.filter(event=event) if event else qs


# ==============================================================================
@python_2_unicode_compatible
class Occurrence(models.Model):
    """
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event = models.ForeignKey(Event, editable=False)
    objects = OccurrenceManager()
    is_multiple = models.BooleanField(default=False)

    # ==========================================================================
    class Meta:
        verbose_name = 'occurrence'
        verbose_name_plural = 'occurrences'
        ordering = ('start_time', 'end_time')

    # --------------------------------------------------------------------------
    def __str__(self):
        return u'{}: {}'.format(self.title, self.start_time.isoformat())

    # --------------------------------------------------------------------------
    def get_absolute_url(self):
        return reverse('topic:get_occurrence', kwargs={'occurrence_id': self.pk})

    def delete_url(self):
        return reverse('topic:crud:delete_occurrence', kwargs={'occurrence_id': self.pk})

    #def update_url(self):
        #return reverse('topic:crud:update_occurrence', kwargs={'occurrence_id': self.pk})

    # --------------------------------------------------------------------------
    def __lt__(self, other):
        return self.start_time < other.start_time

    # -------------------------------------
    # Pas bien sur de ces deux proprietes
    @cached_property
    def title(self):
        return self.event.title

    # --------------------------------------------------------------------------
    @cached_property
    def event_type(self):
        return self.event.event_type