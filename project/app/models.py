from django.db import models
from .utils import class_name

# Create your models here.


class Client(models.Model):
    """
    """

    name = models.CharField(max_length=300)
    address = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return class_name(self)


class Project(models.Model):
    """
    """

    client = models.ForeignKey(Client, blank=True, null=True)

    name = models.CharField(max_length=300, blank=True, null=True)

    end_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return class_name(self)
