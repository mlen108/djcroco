djcroco
=======

.. image:: https://pypip.in/v/djcroco/badge.png
   :target: https://pypi.python.org/pypi/djcroco

.. image:: https://travis-ci.org/mattack108/djcroco.png?branch=master
   :target: https://travis-ci.org/mattack108/djcroco

``djcroco`` is a custom `Django <https://www.djangoproject.com/>`_ model field to
add support for the `Crocodoc API <https://crocodoc.com/>`_.

It behaves like standard `FileField <https://docs.djangoproject.com/en/dev/ref/models/fields/#filefield>`_
so you can still use most of its properties (e.g. ``name``, ``size``, ``url``
etc) while having extra ones to play with Crocodoc API.

``djcroco`` is supported by `Incuna <http://incuna.com>`_ (an awesome company
I work for!).

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


Thumbnail caching
-----------------

By default the thumbnail will be generated every time the template gets rendered.
This could be time expensive if you have e.g 20 items on a single page. To avoid
above issue you can point to a field where the thumbnail will be saved and served
from there the next time.

    class Example(models.Model):
        name = models.CharField(max_length=255)
        document = CrocoField(thumbnail_field='my_thumbnail')
        my_thumbnail = models.ImageField(upload_to='whatever/')

Note that the `thumbnail_field` must be a type of `ImageField`.

Render the awesomeness
----------------------

Documents
^^^^^^^^^

    {{ obj.document.name }}

Returns name of the document.

    {{ obj.document.size }}

Returns size of the document (in bytes).

    {{ obj.document.size_human }}

Returns human-readable size of the document (eg. 1.3 MB).

    {{ obj.document.type }}

Returns type (extension) of the document.

    {{ obj.document.uuid }}

Returns UUID of the document (each Crocodoc document has unique id).

Thumbnails
^^^^^^^^^^

    {{ obj.document.thumbnail }}

Returns thumbnail as inline image (see `Data URI scheme <https://en.wikipedia.org/wiki/Data_URI_scheme>`_ for more details).

URLs
^^^^

    {{ obj.document.url }}

Returns url of the document so it can be viewed directly.

    {{ obj.document.content_url }}

Returns url of the document wrapped in `HttpResponse <https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse>`_ object.

Annotations
^^^^^^^^^^^

    {% url 'croco_document_edit' uuid=obj.document.uuid user_id=<user_id> user_name=<user_name> %}

Returns url of the document to allow user to create annotations.
`See the docs <https://crocodoc.com/docs/walkthrough/comments/>`_ for more details.

    {% url 'croco_document_annotations' uuid=obj.document.uuid user_id=<user_id> %}

Returns url of the document with annotations/comments made by user with given
`user_id`.

Downloads
^^^^^^^^^

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
- Django 1.3.x, 1.4.x, 1.5.x
- `crocodoc <https://pypi.python.org/pypi/crocodoc>`_ 0.1.1

Python 3.x will be supported soon!
