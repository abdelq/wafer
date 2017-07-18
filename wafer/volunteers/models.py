from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from wafer.talks.models import Talk


@python_2_unicode_compatible
class Volunteer(models.Model):

    RATINGS = (
            (0, 'No longer welcome'),
            (1, 'Poor'),
            (2, 'Not great'),
            (3, 'Average'),
            (4, 'Good'),
            (5, 'Superb'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='volunteer')

    tasks = models.ManyToManyField('Task', blank=True)

    staff_rating = models.IntegerField(null=True, blank=True, choices=RATINGS)
    staff_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return u'%s' % self.user


@python_2_unicode_compatible
class Task(models.Model):

    class Meta:
        ordering = ['date', 'start_time', '-end_time', 'name']

    name = models.CharField(max_length=1024)
    description = models.TextField()

    # Date/Time
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Volunteers
    volunteers = models.ManyToManyField('Volunteer', blank=True)
    nbr_volunteers_min = models.IntegerField(default=1)
    nbr_volunteers_max = models.IntegerField(default=1)

    talk = models.ForeignKey(Talk, null=True, blank=True)

    def __str__(self):
        return u'%s (%s: %s - %s)' % (self.name, self.date, self.start_time, self.end_time)

    def nbr_volunteers(self):
        return self.volunteer_set.count()
