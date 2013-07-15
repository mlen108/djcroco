import urlparse
import urllib

from django import template

register = template.Library()


def add_query_params(url, params=None):
    """
    Adds additional query params to the given url, preserving original ones.

    Usage:
    >>> add_query_params('http://foo.com', {'a': 'b'})
    'http://foo.com?a=b'
    >>> add_query_params('http://foo.com/?a=b', {'b': 'c', 'd': 'q'})
    'http://foo.com/?a=b&b=c&d=q'
    """
    if not params:
        return url
    encoded = urllib.urlencode(params)
    url = urlparse.urlparse(url)
    return urlparse.urlunparse((url.scheme, url.netloc, url.path, url.params,
        (encoded if not url.query else url.query + '&' + encoded),
        url.fragment))


# TODO: dynamic creation of filters using python's closures?
@register.filter
def editable(url, editable):
    return add_query_params(url, {'editable': editable})


@register.filter
def user_id(url, user_id):
    return add_query_params(url, {'user_id': user_id})


@register.filter
def user_name(url, user_name):
    return add_query_params(url, {'user_name': user_name})


@register.filter
def user_filter(url, user_filter):
    return add_query_params(url, {'filter': user_filter})


@register.filter
def admin(url, admin):
    return add_query_params(url, {'admin': admin})


@register.filter
def downloadable(url, downloadable):
    return add_query_params(url, {'downloadable': downloadable})


@register.filter
def copyprotected(url, copyprotected):
    return add_query_params(url, {'copyprotected': copyprotected})


@register.filter
def demo(url, demo):
    return add_query_params(url, {'demo': demo})


@register.filter
def sidebar(url, sidebar):
    return add_query_params(url, {'sidebar': sidebar})


@register.filter
def pdf(url, pdf):
    return add_query_params(url, {'pdf': pdf})


@register.filter
def filename(url, filename):
    return add_query_params(url, {'filename': filename})


@register.filter
def annotated(url, annotated):
    return add_query_params(url, {'annotated': annotated})


@register.filter
def size(url, size):
    return add_query_params(url, {'size': size})
