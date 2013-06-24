from django.db import models

from djcroco.fields import CrocoField


class Example(models.Model):
    name = models.CharField(max_length=255)
    document = CrocoField()

    def __unicode__(self):
        return self.name
