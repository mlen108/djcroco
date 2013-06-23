from django.conf.urls import patterns, url

from .views import CrocoDocumentView, CrocoDocumentDownload

urlpatterns = patterns('',
    url(r'^croco_document_view/(?P<uuid>[-\w]+)$',
        CrocoDocumentView.as_view(),
        name='croco_document_view'),
    url(r'^croco_document_download/(?P<uuid>[-\w]+)$',
        CrocoDocumentDownload.as_view(),
        name='croco_document_download'),
)
