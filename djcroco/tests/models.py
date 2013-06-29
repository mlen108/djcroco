from django.db import models

from djcroco.fields import CrocoField


class Example(models.Model):
    name = models.CharField(max_length=255)
    document = CrocoField()

    def __unicode__(self):
        return self.name


class ThumbnailExample(models.Model):
    name = models.CharField(max_length=255)
    document = CrocoField(thumbnail_field='thumbnail')
    thumbnail = models.ImageField(upload_to='whatever/')

    def __unicode__(self):
        return self.name
