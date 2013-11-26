import base64
import json
import os

from django import forms, get_version
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

if get_version()[:5] < '1.4.2':  # six was added in 1.4.2
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
        return self._url_for('croco_document_url')

    @property
    def content_url(self):
        return self._url_for('croco_document_content_url')

    @property
    def download_document(self):
        return self._url_for('croco_document_download')

    @property
    def download_thumbnail(self):
        return self._url_for('croco_thumbnail_download')

    @property
    def download_text(self):
        return self._url_for('croco_text_download')

    def _url_for(self, url):
        return reverse(url, kwargs={'uuid': self.attrs['uuid']})

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
        self.thumbnail_field = kwargs.pop('thumbnail_field', None)
        super(CrocoField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value == "":
            return value

        try:
            if isinstance(value, string_types):
                return CrocoFieldObject(self, json.loads(value))
        except ValueError:
            raise
        return value

    def pre_save(self, model_instance, add):
        value = super(CrocoField, self).pre_save(model_instance, add)
        if value and not isinstance(value, CrocoFieldObject):
            croco_uuid = self.storage._save(value)
            file_attrs = {
                'name': value.name,
                'size': value.size,
                'uuid': croco_uuid,
                'type': self._file_ext(value.name),
            }
            value = CrocoFieldObject(self, file_attrs)

            # if self.thumbnail_field:
            #     thumbnail = model_instance._meta.get_field(self.thumbnail_field)
            #     filename = thumbnail.upload_to + croco_uuid
            #     thumbnail.storage.delete(filename)
        return self.get_prep_value(value)

    def contribute_to_class(self, cls, name):
        super(CrocoField, self).contribute_to_class(cls, name)
        if self.thumbnail_field:
            signals.post_init.connect(self._check_thumbnail_field, sender=cls)

    def _check_thumbnail_field(self, instance, force=False, *args, **kwargs):
        obj = instance._meta
        if not self.thumbnail_field in obj.get_all_field_names():
            msg = "No field '{0}' found on '{1}' class."
            raise AttributeError(msg.format(self.thumbnail_field, obj.object_name))

        field = obj.get_field(self.thumbnail_field)
        if not isinstance(field, models.ImageField):
            msg = "Field '{0}' must be an instance of '{1}'."
            raise AttributeError(msg.format(self.thumbnail_field, models.ImageField))

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

    # This is copied from models.FileField
    def save_form_data(self, instance, data):
        # Important: None means "no change", other false value means "clear"
        # This subtle distinction (rather than a more explicit marker) is
        # needed because we need to consume values that are also sane for a
        # regular (non Model-) Form to find in its cleaned_data dictionary.
        if data is not None:
            # This value will be converted to unicode and stored in the
            # database, so leaving False as-is is not acceptable.
            if not data:
                data = ''
            setattr(instance, self.name, data)

    def _get_thumbnail(self, uuid):
        if self.thumbnail_field:
            thumbnail = self.model._meta.get_field(self.thumbnail_field)
            filename = thumbnail.upload_to + uuid
            # TODO: try to avoid using `exists` as it is expensive to check
            if thumbnail.storage.exists(filename):
                return thumbnail.storage.url(filename)

        try:
            status = crocodoc.document.status(uuid)
            if status.get('error') is None:
                try:
                    attrs = {
                        'width': self.thumbnail_size[0],
                        'height': self.thumbnail_size[1],
                    }
                    thumbnail = crocodoc.download.thumbnail(uuid, **attrs)
                    if not self.thumbnail_field:
                        return "data:image/png;base64," + base64.b64encode(thumbnail)

                    return self._save_thumbnail(uuid, thumbnail)
                except CrocodocError as e:
                    return e.error_message
            else:
                return status.get('error')
        except CrocodocError as e:
            return e.error_message

    def _save_thumbnail(self, uuid, thumbnail):
        # TODO: does it need to be written to temp file?
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(thumbnail)
        img_temp.seek(0)
        img_temp.flush()

        thumbnail_field = self.model._meta.get_field(self.thumbnail_field)

        filename = thumbnail_field.upload_to + uuid
        thumbnail_field.storage.save(filename, File(img_temp))

        return thumbnail_field.storage.url(filename)

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
