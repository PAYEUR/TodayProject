# coding=utf-8
import re
from datetime import datetime
from dateutil import rrule

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

__all__ = (
    'Note',
    'EventType',
    'Event',
    'Occurrence',
    'City',
)

# ==============================================================================
@python_2_unicode_compatible
class City(models.Model):
    """ Place class. Use to make queries on city.
    """

    city_name = models.CharField(_('city_name'), max_length=255, default="Paris")
    #location = PlainLocationField(based_fields=['city_name'], zoom=7, default="Null")

    # ==========================================================================
    class Meta:
        verbose_name =_('city')
        verbose_name_plural =_('cities')

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.city_name


# ==============================================================================
@python_2_unicode_compatible
class Note(models.Model):
    """
    A generic model for adding simple, arbitrary notes to other models such as
    ``Event`` or ``Occurrence``.
    """
    note = models.TextField(_('note'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = GenericForeignKey('content_type', 'object_id')

    # ==========================================================================
    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.note


# ==============================================================================
@python_2_unicode_compatible
class EventType(models.Model):
    """
    Simple ``Event`` classifcation.
    """

    label = models.CharField(_('label'), max_length=50)
    image = models.ImageField(default=None, upload_to='event_types/')

    # ==========================================================================
    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')

    # --------------------------------------------------------------------------
    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('event_type_coming_days', kwargs={'event_type_id': self.pk})


# ==============================================================================
@python_2_unicode_compatible
class Event(models.Model):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'))
    event_type = models.ForeignKey(EventType, verbose_name=_('event type'))
    notes = GenericRelation(Note, verbose_name=_('notes'))
    image = models.ImageField(default=None, upload_to='events/')
    price = models.PositiveSmallIntegerField(default=0)
    #For the moment one limits choices to Paris
    city = models.ForeignKey(City, default={'city_name': "Paris"},)#limit_choices_to={'city_name': "Paris"},)
    address = models.CharField(_('address'), max_length=150, default="non precisé")

    # ===========================================================================
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title', )

    # ---------------------------------------------------------------------------
    def __str__(self):
        return self.title

    # --------------------------------------------------------------------------
    def get_absolute_url(self):
        return reverse('get_event', kwargs={'event_id': self.pk})

    # --------------------------------------------------------------------------
    def add_occurrences(self, start_time, end_time, **rrule_params):
        """
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        """
        count = rrule_params.get('count')
        until = rrule_params.get('until')
        if not (count or until):
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            rrule_params.setdefault('freq', rrule.DAILY)
            delta = end_time - start_time
            occurrences = []
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(Occurrence(start_time=ev, end_time=ev + delta, event=self))
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
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    event = models.ForeignKey(Event, verbose_name=_('event'), editable=False)
    notes = GenericRelation(Note, verbose_name=_('notes'))

    objects = OccurrenceManager()

    # ==========================================================================
    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        ordering = ('start_time', 'end_time')

    # --------------------------------------------------------------------------
    def __str__(self):
        return u'{}: {}'.format(self.title, self.start_time.isoformat())

    # --------------------------------------------------------------------------
    @models.permalink
    def get_absolute_url(self):
        return ('swingtime-occurrence', [str(self.event.id), str(self.id)])

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


# ==============================================================================
# some research functions, after http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap


def normalize_query(query_string,
                findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                normspace=re.compile(r'\s{2,}').sub):
    """ Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.

    """
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """ Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    """
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = models.Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query