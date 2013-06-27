from django import get_version

if get_version()[:3] == '1.3':
    from django.conf.urls.defaults import patterns, include, url
else:
    from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'', include('djcroco.urls')),
)
