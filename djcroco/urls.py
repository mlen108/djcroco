from django import get_version

if get_version()[:3] == '1.3':
    from django.conf.urls.defaults import patterns, include, url
else:
    from django.conf.urls import patterns, include, url


import views

urlpatterns = patterns('',
    url(r'^croco_document/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentView.as_view(redirect=True),
        name='croco_document_url'),
    url(r'^croco_document_content/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentView.as_view(),
        name='croco_document_content_url'),
    url(r'^croco_document_download/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentDownload.as_view(),
        name='croco_document_download'),
    url(r'^croco_thumbnail_download/(?P<uuid>[-\w]+)$',
        views.CrocoThumbnailDownload.as_view(),
        name='croco_thumbnail_download'),
    url(r'^croco_text_download/(?P<uuid>[-\w]+)$',
        views.CrocoTextDownload.as_view(),
        name='croco_text_download'),
)
