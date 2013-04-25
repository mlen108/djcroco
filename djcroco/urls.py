from django.conf import settings
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import CrocoDownload, CrocoView

urlpatterns = patterns('',
    url(r'^croco_view/(?P<pk>\d+)/$', CrocoView.as_view(), name='croco_view'),
    url(r'^croco_download/(?P<pk>\d+)/$', CrocoDownload.as_view(), name='croco_download'),
)
