djcroco
=======

.. image:: https://pypip.in/v/djcroco/badge.png
   :target: https://pypi.python.org/pypi/djcroco

.. image:: https://travis-ci.org/mattack108/djcroco.png
   :target: https://travis-ci.org/mattack108/djcroco

djcroco is a custom `Django <https://www.djangoproject.com/>`_ model field to
add support for the `Crocodoc API <https://crocodoc.com/>`_.

Installation
------------

To install ``djcroco``, simply run: ::

    pip install djcroco

Include in ``urls.py``: ::

    url(r'', include('djcroco.urls')),

Define Crocodoc API token in ``settings.py``: ::

    CROCO_API_TOKEN = '<api_token>'

Or alternatively as env variable: ::

    export CROCO_API_TOKEN='<api_token>'

Usage
-----

Define the field in model you wish to extend: ::

    from django.db import models

    from djcroco.fields import CrocoField


    class Example(models.Model):
        name = models.CharField(max_length=255)
        document = CrocoField()

        def __unicode__(self):
            return self.name


Custom thumbnails size
----------------------

You can pass ``thumbnail_size`` like so: ::

    document = CrocoField(thumbnail_size=(150, 150))

Where tuple is represented as ``(width, height)``.

If you do not pass custom thumbnail size, the default will be used (100x100).
The maximum dimensions for thumbnail is 300x300.

Render the awesomeness
----------------------

    {{ obj.document.name }}

Returns name of the file.

    {{ obj.document.size }}

Returns size of the file (in bytes).

    {{ obj.document.size_human }}

Returns human-readable size of the file (eg. 1.3 MB).

    {{ obj.document.type }}

Returns type (extension) of the file.

    {{ obj.document.uuid }}

Returns UUID of the file (each Crocodoc document has unique id).

    {{ obj.document.thumbnail }}

Returns thumbnail as inline image (see `Data URI scheme <https://en.wikipedia.org/wiki/Data_URI_scheme>`_ for more details).

    {{ obj.document.url }}

Returns url of the file so document can be viewed directly.

    {{ obj.document.content_url }}

Returns url of the file wrapped in `HttpResponse <https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse>`_ object.

    {{ obj.document.download_document }}

Returns the original document in PDF format.

    {{ obj.document.download_thumbnail }}

Returns a thumbnail of the document's first page in PNG format.

    {{ obj.document.download_text }}

Returns the full text from a document.
Note: This method is available only if your Crocodoc account has text
extraction enabled.

Dependencies
------------

- Python 2.6.x, 2.7.x
- Django 1.4.x, 1.5.x
- `crocodoc <https://pypi.python.org/pypi/crocodoc>`_ 0.1.1

Django 1.3.x and/or Python 3.x will be supported soon!
