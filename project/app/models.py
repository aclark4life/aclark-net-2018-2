from django.db import models
from .utils import class_name_pk

# Create your models here.


class Client(models.Model):
    """
    """
    name = models.CharField(max_length=300)
    address = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Contract(models.Model):
    """
    """

    def __unicode__(self):
        return class_name_pk(self)


class Estimate(models.Model):
    """
    """
    client = models.ForeignKey(Client)

    def __unicode__(self):
        return class_name_pk(self)


class Invoice(models.Model):
    """
    """
    project = models.ForeignKey('Project')

    def __unicode__(self):
        return class_name_pk(self)


class Task(models.Model):
    """
    """
    description = models.TextField(blank=True, null=True)
    entry = models.DurationField(default='01:00', blank=True, null=True)

    client = models.ForeignKey(Client, blank=True, null=True)
    project = models.ForeignKey('Project', blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Project(models.Model):
    """
    """
    name = models.CharField(max_length=300)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    client = models.ForeignKey(Client)

    def __unicode__(self):
        return self.name
