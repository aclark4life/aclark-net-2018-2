from django.db import models
from .utils import class_name

# Create your models here.


class Client(models.Model):
    """
    """

    name = models.CharField(max_length=30)
    address = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return class_name(self)
