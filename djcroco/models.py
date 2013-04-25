import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import filesizeformat

import crocodoc
from crocodoc import CrocodocError

CROCO_MODEL = getattr(settings, 'CROCO_MODEL', None)
if CROCO_MODEL is None:
    raise ImproperlyConfigured("CROCO_MODEL setting is required."
        " Define it in your project's settings.py")

CROCO_API_TOKEN = getattr(settings, 'CROCO_API_TOKEN', None)
if CROCO_API_TOKEN is None:
    raise ImproperlyConfigured("CROCO_API_TOKEN setting is required."
        " Define it in your project's settings.py")

crocodoc.api_token = CROCO_API_TOKEN


class CrocoModel(models.Model):
    crocodoc_uuid = models.CharField(max_length=255, editable=False)
    file_size = models.IntegerField(default=0, editable=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.crocodoc_uuid

    def __init__(self, *args, **kwargs):
        super(CrocoModel, self).__init__(*args, **kwargs)

        no_field = "Define field called '{0}' of type '{1}' in your model."
        wrong_field = "Field '{0}' must be an instance of '{1}'."

        if not hasattr(self, 'file'):
            raise AttributeError(no_field.format('file', 'FileField'))
            if not isinstance(self.file, models.FileField):
                raise AttributeError(wrong_field.format('file', 'FileField'))

        if not hasattr(self, 'thumbnail'):
            raise AttributeError(no_field.format('thumbnail', 'ImageField'))
            if not isinstance(self.thumbnail, models.ImageField):
                raise AttributeError(wrong_field.format('thumbnail', 'ImageField'))

    def save(self, *args, **kwargs):
        # reset thumbnail when re-saving object
        self.thumbnail = None
        # computing size of file everywhere else is expensive
        self.file_size = self.file.size
        # need to save before we save the file.
        super(CrocoModel, self).save(*args, **kwargs)

        # do not upload image as it won't work with Crocodoc
        if self.is_image():
            return

        if not self.is_document():
            return

        if self.file and not self.thumbnail:
            try:
                uuid = crocodoc.document.upload(file=self.file)
            except CrocodocError as e:
                raise AttributeError(e.error_message)

            self.crocodoc_uuid = uuid
            super(CrocoModel, self).save(*args, **kwargs)

    def get_absolute_view_url(self):
        return reverse('croco_view', kwargs={'pk': self.pk})

    def get_absolute_download_url(self):
        return reverse('croco_download', kwargs={'pk': self.pk})

    def get_thumbnail(self):
        # do not ask for thumbnail again if we have one already
        if self.thumbnail:
            return self.thumbnail.url

        # TODO: generate thumbnail for images, till Crocodoc does it
        if self.is_image():
            return self.thumbnail

        # this is nasty code, so make it better soon
        try:
            status = crocodoc.document.status(self.crocodoc_uuid)
            print status
            if status.get('error') is None:
                try:
                    # TODO: custom thumbnail sizes
                    thumbnail = crocodoc.download.thumbnail(self.crocodoc_uuid)
                    self._save_thumbnail(thumbnail)
                except CrocodocError as e:
                    raise AttributeError(e.error_message)
            else:
                raise AttributeError(status['error'])
        except CrocodocError as e:
            raise AttributeError(e.error_message)

        if hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        return self.thumbnail

    def _save_thumbnail(self, thumbnail):
        if thumbnail:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(thumbnail)
            img_temp.seek(0)
            img_temp.flush()

            # TODO: save in original format?
            filename = '{0}.png'.format(img_temp.name.split('/')[-1])

            self.thumbnail = filename
            self.thumbnail.save(
                filename,
                File(img_temp),
                save=True)

            super(CrocoModel, self).save()

    def is_document(self):
        allowed_docs = ('pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx',
            'csv')
        _root, ext = os.path.splitext(self.file.name.lower())
        if ext[1:] in allowed_docs:
            return True

        return False

    def is_image(self):
        """ Check if the file is an image. """

        # TODO: support more types!
        allowed_exts = ('png', 'jpg', 'jpeg', 'gif')
        _root, ext = os.path.splitext(self.file.name.lower())
        if ext[1:] in allowed_exts:
            return True

        return False

    @property
    def is_viewable(self):
        return self.is_document()

    @property
    def is_downloadable(self):
        return True

    @property
    def human_file_size(self):
        """ Return a size of the file """

        return filesizeformat(self.file_size)

    @property
    def file_ext(self):
        """ Return an extension of the file """
        return os.path.splitext(self.file.name)[1][1:]
