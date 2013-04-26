djcroco
=======

djcroco extends your `Django <https://www.djangoproject.com/>`_ model to add support for the `Crocodoc API <https://crocodoc.com/>`_.

Installation
------------

To install ``djcroco``, simply run: ::

    pip install djcroco

Then include in ``urls.py``: ::

    url(r'', include('djcroco.urls')),

And define Crocodoc API token and the model you want to extend.

In ``settings.py``: ::

    CROCO_MODEL = 'app_name.model_name'
    CROCO_API_TOKEN = '<api_token>'

Or in ``env.sh``: ::

    export $CROCO_MODEL='app_name.model_name'
    export $CROCO_API_TOKEN='<api_token>'

Usage
-----

Define the model you wish to extend: ::

    from django.db import models

    from djcroco.models import CrocoModel


    class Example(CrocoModel):
        name = models.CharField(max_length=255)
        file = models.FileField(upload_to='examples/')
        thumbnail = models.ImageField(upload_to='examples/thumbnails/', blank=True,
            null=True, editable=False)

        def __unicode__(self):
            return self.name

**Note:**

* ``CrocoModel`` is an `abstract model <https://docs.djangoproject.com/en/dev/topics/db/models/#abstract-base-classes>`_.

* Your model must contain the above fields of ``file`` and ``thumbnail``, and exactly the same field instances as in the example.

**How it works:**

* Every time you save your model, the ``djcroco`` uploads document to Crocodoc to start conversion process. Only `supported documents <http://support.crocodoc.com/customer/portal/articles/515434-what-file-formats-are-supported->`_ are uploaded.

* When the template renders, the ``get_thumbnail`` method creates a thumbnail to display in your app.

* The ``get_absolute_view_url`` creates a viewing session on Crocodoc so you can embed the document in your app. It returns only an URL so it is up to you how you use it.


Render the awesomeness in your template: ::

    <ul>
    {% for obj in object_list %}
        <li>Name: {{ obj.name }}</li>
        <li>Size: {{ obj.human_file_size }}</li>
        <li>Extension: {{ obj.file_ext }}</li>
        <li><img src="{{ obj.get_thumbnail }}"></li>

        {% if obj.is_viewable %}
        <li><a href="{{ obj.get_absolute_view_url }}">View</a></li>
        {% endif %}

        {% if obj.is_downloadable %}
        <li><a href="{{ obj.get_absolute_download_url }}">Download</a></li>
        {% endif %}
    {% endfor %} 
    </ul>



Dependencies
------------

``djcroco`` depends only on `crocodoc-python <https://github.com/crocodoc/crocodoc-python>`_ in order to communicate with Crocodoc API service.

Limitations
-----------

``djcroco`` was tested on Django 1.4/Python 2.7.3. Other versions of Django/Python will be supported soon.
