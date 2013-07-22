djcroco
=======

.. image:: https://travis-ci.org/mattack108/djcroco.png?branch=master
   :target: https://travis-ci.org/mattack108/djcroco

.. image:: https://pypip.in/v/djcroco/badge.png
   :target: https://pypi.python.org/pypi/djcroco

.. image:: https://pypip.in/d/djcroco/badge.png
   :target: https://pypi.python.org/pypi/djcroco

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

When optional parameters for URLs are used (see below for more details) - then
you need to add ``djcroco`` to ``INSTALLED_APPS``: ::

    INSTALLED_APPS += ('djcroco',)

And load its template tags in the template you wish to use them in: ::

    {% load croco_tags %}

Usage
-----

Define the field in model you wish to extend:

.. code-block:: python

    from django.db import models

    from djcroco.fields import CrocoField


    class Example(models.Model):
        name = models.CharField(max_length=255)
        document = CrocoField()

        def __unicode__(self):
            return self.name


Custom thumbnails size
----------------------

You can pass ``thumbnail_size`` like so:

.. code-block:: python

    document = CrocoField(thumbnail_size=(150, 150))

Where tuple is represented as *(width, height)*.

If you do not pass custom thumbnail size, the default will be used (100x100).
The maximum dimensions for thumbnail is **300x300**.


Thumbnail caching
-----------------

By default the thumbnail will be generated every time template gets rendered and
this involves hitting Crocodoc API for each thumbnail. It could be time
expensive if you have many items on a single page. To avoid above issue you
can point to a field where the thumbnail will be saved and served from there
the next time.

.. code-block:: python

    class Example(models.Model):
        name = models.CharField(max_length=255)
        document = CrocoField(thumbnail_field='my_thumbnail')
        my_thumbnail = models.ImageField(upload_to='whatever/')


Note that the ``thumbnail_field`` must be a type of `ImageField 
<https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield>`_.

Render the awesomeness
----------------------

Documents
^^^^^^^^^

::

    {{ obj.document.name }}

Returns name of the document.

::

    {{ obj.document.size }}

Returns size of the document (in bytes).

::

    {{ obj.document.size_human }}

Returns human-readable size of the document (eg. 1.3 MB).

::

    {{ obj.document.type }}

Returns type (extension) of the document.

::

    {{ obj.document.uuid }}

Returns UUID of the document (note: each Crocodoc document has unique id).

Thumbnails
^^^^^^^^^^

::

    {{ obj.document.thumbnail }}

Returns thumbnail as inline image (see `Data URI scheme <https://en.wikipedia.org/wiki/Data_URI_scheme>`_ for more details). See below for how to download a thumbnail.

URLs
^^^^

::

    {{ obj.document.url }}

Returns url of the document so it can be viewed directly.

::

    {{ obj.document.content_url }}

Returns url of the document wrapped in `HttpResponse 
<https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse>`_ object.

Both ``url`` and ``content_url`` can be extended with `optional parameters <https://crocodoc.com/docs/api/#session-create>`_.

::

    {{ obj.document.url|editable:"true"|user_id:"1"|user_name:"admin" }}

``editable`` param allows users to create annotations and comments while viewing the document.
**Default: false**

``user_id`` and ``user_name`` will be shown in the viewer to attribute annotations and comments to their author. **Required if editable is true**

::

    {{ obj.document.url|user_filter:"1,2,3" }}

Limits which users' annotations and comments are shown. Possible values are: *all*, *none*, or a comma-separated list of user IDs. **Default: all**

**Note**: ``user_filter`` is a renamed version of Crocodoc's ``filter`` in order to work in Django template system.

Full list of supported `parameters <https://crocodoc.com/docs/api/#session-create>`_.

Downloads
^^^^^^^^^

::

    {{ obj.document.download_document }}

Returns the original document in PDF format.

::

    {{ obj.document.download_document|annotated:"true" }}

Returns the original document with annotations. **Default: false**

::

    {{ obj.document.download_document|user_filter:"1,2,3" }}

Returns the original document with annotations limited to given users.
Possible values are: *all*, *none*, or a comma-separated list of user IDs. **Default: all**

::

    {{ obj.document.download_thumbnail }}

Returns a thumbnail of the document's first page in PNG format.

::

    {{ obj.document.download_thumbnail|size:"99x99" }}

Same as ``download_thumbnail`` with custom dimensions of the thumbnail in the format *{width}x{height}*. Largest dimensions allowed are 300x300. **Default: 100x100**

::

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
