from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible  # only if you need to support Python 2
class AllJobIDs(models.Model):
    JobStatus = (
        ('0', 'to be start'),
        ('1', 'running'),
        ('2', 'finished'),
        ('3', 'something wrong'),
    )


    JobID = models.PositiveIntegerField(blank=True, default=0)
    JobType = models.CharField(max_length=50, default='')
    SubJobType = models.CharField(max_length=50, default='')
    CPUs = models.PositiveIntegerField(blank=True, default=0)
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    CreatedDate = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.pk)

@python_2_unicode_compatible  # only if you need to support Python 2
class StatisticsData(models.Model):
    IP = models.CharField(max_length=20, default='')
    IPType = models.CharField(max_length=20, default='')
    PagesVisted = models.CharField(max_length=200, default='')
    Date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.pk)
