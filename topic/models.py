# coding=utf-8

from datetime import datetime

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.core.urlresolvers import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from connection.models import EnjoyTodayUser
from location.models import City

__all__ = (
    'EventType',
    'Event',
    'Occurrence',
)


# ==============================================================================
@python_2_unicode_compatible
class Topic(models.Model):
    """
    topic class, for example "catho" or "jobs"
    the name has to be the same as the corresponding namespace
    """
    name = models.CharField(verbose_name="Thématique",
                            max_length=50,
                            default='spi')

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.name


# ==============================================================================
@python_2_unicode_compatible
class EventType(models.Model):
    """
    Simple ``Event`` classification.
    """
    topic = models.ForeignKey(Topic,
                              verbose_name='Thematique',
                              default=None,
                              null=True,
                              on_delete=models.SET_DEFAULT)

    label = models.CharField(verbose_name='label',
                             max_length=50,
                             default='autres')

    image = models.ImageField(default=None,
                              null=True,
                              upload_to='event_types/')

    # ==========================================================================
    class Meta:
        verbose_name = 'event type'
        verbose_name_plural = 'event types'

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.label

    # Impossible to define get_absolute_url because location can't be retrieved from here


# ==============================================================================
@python_2_unicode_compatible
class Event(models.Model):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """

    # null = True:empty bdd field allowed to be "NULL" instead of no_string. Not good in django
    # blank = True: validation thing: not required if True
    # see also https://docs.djangoproject.com/fr/1.10/ref/models/fields/

    image = models.ImageField(verbose_name="Image",
                              upload_to='events/',
                              help_text="image affichée pour l'événement",
                              default=None
                              )

    title = models.CharField(verbose_name="Titre",
                             max_length=100,
                             help_text="Titre affiché pour l'événement",
                             default=None,
                             )

    description = models.TextField(verbose_name="Description",
                                   help_text="Description de l'événement. Ajouter également tout détails utiles",
                                   default=None
                                   )

    event_type = models.ForeignKey(EventType,
                                   verbose_name="Catégorie",
                                   on_delete=models.SET_DEFAULT,
                                   help_text="Catégorie à laquelle est rattaché l'événement",
                                   default=None,
                                   )

    price = models.CharField(verbose_name="Prix",
                             max_length=300,
                             blank=True,
                             help_text="Conditions tarifaires",
                             default=None,
                             )

    contact = models.CharField(verbose_name="Détails organisateur",
                               max_length=150,
                               blank=True,
                               help_text="Informations sur l'organisateur <u>officiel</u> de l'événement",
                               default=None,
                               )

    address = models.CharField(verbose_name="Adresse",
                               max_length=150,
                               help_text="Donner l'adresse postale <u>au sens de google</u>",
                               default=None,
                               )

    public_transport = models.CharField(verbose_name="Transport en commun",
                                        max_length=150,
                                        blank=True,
                                        help_text="Arrêt de métro,...",
                                        default=None,
                                        )

    location = models.ForeignKey(City,
                                 on_delete=models.SET_DEFAULT,
                                 help_text="ville dans laquelle sera posté l'événement",
                                 default=None,
                                 )

    # auto filled fields
    event_planner = models.ForeignKey(EnjoyTodayUser,
                                      on_delete=models.CASCADE,
                                      verbose_name='annonceur',
                                      default=None,
                                      blank=True,
                                      )

    created_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Date de création",
                                      )

    # Resize image
    image_main = ImageSpecField(source='image',
                                processors=[ResizeToFill(800, 300)],
                                format='JPEG',
                                options={'quality': 100},
                                )

    # ===========================================================================
    class Meta:
        verbose_name = 'event'
        verbose_name_plural = 'events'
        ordering = ('title', )

    # ---------------------------------------------------------------------------
    def __str__(self):
        return self.title

    # --------------------------------------------------------------------------
    def delete_url(self):
        return reverse('crud:delete_event', kwargs={'event_id': self.pk})

    def update_url(self):
        return reverse('crud:update_event', kwargs={'event_id': self.pk})

    def add_occurrences_url(self):
        return reverse('crud:add_occurrences', kwargs={'event_id': self.pk})

    # --------------------------------------------------------------------------
    def add_occurrences(self, datetime_list, delta_hour, is_multiple):
        """
        :param datetime_list: list of datetimes
        :param delta_hour: duration of the occurrence
        :param is_multiple: bool
        :return: Add occurrences (usually multiples ones) to an event
        """

        occurrences = []
        for ev in datetime_list:
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
    event = models.ForeignKey(Event,
                              # TODO: determine why editable=False (not accessible in admin...)
                              editable=False,
                              on_delete=models.CASCADE)
    objects = OccurrenceManager()
    is_multiple = models.BooleanField(default=False)

    # ==========================================================================
    class Meta:
        verbose_name = 'occurrence'
        verbose_name_plural = 'occurrences'
        ordering = ('start_time', 'end_time')

    # --------------------------------------------------------------------------
    def __str__(self):
        return u'{}: {}'.format(self.event.title, self.start_time.isoformat())

    # --------------------------------------------------------------------------
    def get_absolute_url(self):
        return reverse('location:topic:get_occurrence',
                       kwargs={'pk': self.pk,
                               'city_slug': self.event.location.city_slug,
                               'topic_name': self.event.event_type.topic.name
                               }
                       )

    def get_events_for_same_day_url(self):
        return reverse('location:topic:daily_events',
                       kwargs={'year': str(self.start_time.year),
                               'month': str(self.start_time.month),
                               'day': str(self.start_time.day),
                               'city_slug': self.event.location.city_slug,
                               'topic_name': self.event.event_type.topic.name
                               }
                       )

    def delete_url(self):
        return reverse('crud:delete_occurrence',
                       kwargs={'occurrence_id': self.pk},
                       )

    def update_url(self):
        return reverse('crud:update_occurrence',
                       kwargs={'occurrence_id': self.pk},
                       )

    # --------------------------------------------------------------------------
    def __lt__(self, other):
        return self.start_time < other.start_time
