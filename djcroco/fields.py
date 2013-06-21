import datetime
import os

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
# from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.db.models.fields.files import FieldFile, FileDescriptor
from django.template.defaultfilters import filesizeformat
from django.utils import six
from django.utils.translation import ugettext_lazy as _

import crocodoc
from crocodoc import CrocodocError

_token = 'CROCO_API_TOKEN'
CROCO_API_TOKEN = getattr(settings, _token, os.environ.get(_token))
if CROCO_API_TOKEN is None:
    raise ImproperlyConfigured("CROCO_API_TOKEN setting is required."
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

    def delete(self, name):
        return 'delete'

    def size(self, name):
        from django.template.defaultfilters import filesizeformat
        return filesizeformat(self._file_size)

    def url(self, name):
        return getattr(self, '_croco_uuid')


class CrocoField(models.Field):
    attr_class = FieldFile
    descriptor_class = FileDescriptor
    description = _("CrocoField")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        self.storage = CrocoStorage()
        super(CrocoField, self).__init__(verbose_name, name, **kwargs)

    def get_internal_type(self):
        return "FileField"

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, 'name'):
            value = value.name
        return super(CrocoField, self).get_prep_lookup(lookup_type, value)

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        # Need to convert File objects provided via a form to unicode for database insertion
        if value is None:
            return None
        return six.text_type(value)

    def pre_save(self, model_instance, add):
        file = super(CrocoField, self).pre_save(model_instance, add)
        self.storage._save(file)
        return file

    def contribute_to_class(self, cls, name):
        super(CrocoField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        print '!' * 200
        1/0
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))

    def clean(self, instance, filename):
        if not self._is_document(instance.name):
            raise forms.ValidationError("Unsupported file type.")
        return super(CrocoField, self).clean(instance, filename)

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

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.FileField}
        defaults.update(kwargs)
        return super(CrocoField, self).formfield(**defaults)

    def _file_ext(self, filename):
        """ Return an extension of the file """
        return os.path.splitext(filename)[1][1:]

    def _is_document(self, filename):
        _root, ext = os.path.splitext(filename.lower())
        if ext[1:] in ('pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'csv'):
            return True
        return False


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^djcroco\.fields\.CrocoField"])
except ImportError:
    pass
