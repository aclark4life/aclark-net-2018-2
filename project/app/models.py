from django.db import models

# Create your models here.


class Client(models.Model):
    """
    """

    def __unicode__(self):
        return '-'.join([self.__class__.__name__, str(self.pk)])
