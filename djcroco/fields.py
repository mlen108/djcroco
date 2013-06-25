import base64
import json
import os

from django import forms, get_version
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

if get_version()[:3] == '1.3':
    string_types = basestring
else:
    from django.utils.six import string_types

import crocodoc
from crocodoc import CrocodocError

_token = 'CROCO_API_TOKEN'
CROCO_API_TOKEN = getattr(settings, _token, os.environ.get(_token))
if CROCO_API_TOKEN is None:
    raise ImproperlyConfigured("CROCO_API_TOKEN settings is required."
        " Define it in your project's settings.py or env.sh file.")

crocodoc.api_token = CROCO_API_TOKEN


class CrocoStorage(Storage):
    def __init__(self):
        self._croco_uuid = None

    def get_valid_name(self, name):
        from django.utils.text import get_valid_filename
        return get_valid_filename(name)

    def _save(self, file):
        try:
            uuid = crocodoc.document.upload(file=file)
            setattr(self, '_croco_uuid', uuid)
        except CrocodocError as croco_error:
            raise croco_error

        return uuid


class CrocoFieldObject(object):
    def __init__(self, instance, attrs):
        self.instance = instance
        self.attrs = attrs

    def __getattr__(self, name):
        if name in self.attrs:
            return self.attrs[name]
        return name

    @property
    def size_human(self):
        return filesizeformat(self.attrs['size'])

    @property
    def thumbnail(self):
        return self.instance._get_thumbnail(self.attrs['uuid'])

    @property
    def url(self):
        return reverse('croco_document_view', kwargs={
            'uuid': self.attrs['uuid']
        })

    @property
    def content_url(self):
        return reverse('croco_document_content', kwargs={
            'uuid': self.attrs['uuid']
        })

    def edit_url(self, user_id, user_name):
        return reverse('croco_document_edit', kwargs={
            'uuid': self.attrs['uuid'],
            'user_id': user_id,
            'user_name': user_name,
        })

    def annotations_url(self, user_id):
        return reverse('croco_document_annotations', kwargs={
            'uuid': self.attrs['uuid'],
            'user_id': user_id,
        })

    @property
    def download_document(self):
        return reverse('croco_document_download', kwargs={
            'uuid': self.attrs['uuid']
        })

    @property
    def download_thumbnail(self):
        return reverse('croco_thumbnail_download', kwargs={
            'uuid': self.attrs['uuid']
        })

    @property
    def download_text(self):
        return reverse('croco_text_download', kwargs={
            'uuid': self.attrs['uuid']
        })

    def __unicode__(self):
        return "%s" % self.attrs['name']

    def __str__(self):
        return "%s" % self.attrs['name']


class CrocoField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = _("CrocoField")

    def __init__(self, verbose_name=None, name=None, *args, **kwargs):
        self.storage = CrocoStorage()
        self.thumbnail_size = kwargs.pop('thumbnail_size', (100, 100))
        super(CrocoField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value == "":
            return None

        try:
            if isinstance(value, string_types):
                return CrocoFieldObject(self, json.loads(value))
        except ValueError:
            raise
        return value

    def pre_save(self, model_instance, add):
        value = super(CrocoField, self).pre_save(model_instance, add)
        if not isinstance(value, CrocoFieldObject):
            croco_uuid = self.storage._save(value)
            file_attrs = {
                'name': value.name,
                'size': value.size,
                'uuid': croco_uuid,
                'type': self._file_ext(value.name),
            }
            value = CrocoFieldObject(self, file_attrs)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if isinstance(value, CrocoFieldObject):
            return json.dumps(value.attrs)
        return value

    def clean(self, instance, filename):
        if not self._is_document(instance.name):
            raise forms.ValidationError("Unsupported file type.")
        return super(CrocoField, self).clean(instance, filename)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.FileField}
        defaults.update(kwargs)
        return super(CrocoField, self).formfield(**defaults)

    def _get_thumbnail(self, uuid):
        """
        Returns in-line image using URI scheme.
        TODO: add support for custom image field (so thumbnails are cached)
        """
        try:
            status = crocodoc.document.status(uuid)
            if status.get('error') is None:
                try:
                    attrs = {
                        'width': self.thumbnail_size[0],
                        'height': self.thumbnail_size[1],
                    }
                    thumb = crocodoc.download.thumbnail(uuid, **attrs)
                    return "data:image/png;base64," + base64.b64encode(thumb)
                except CrocodocError as e:
                    return e.error_message
            else:
                return status.get('error')
        except CrocodocError as e:
            return e.error_message

    def _file_ext(self, filename):
        """ Return an extension of the file """
        return os.path.splitext(filename)[1][1:]

    def _is_document(self, filename):
        allowed_exts = ('pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx',
            'csv')
        _root, ext = os.path.splitext(filename.lower())
        if ext[1:] in allowed_exts:
            return True
        return False

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^djcroco\.fields\.CrocoField"])
