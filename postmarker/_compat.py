# coding: utf-8


try:
    from urllib.parse import urljoin
except ImportError:  # Python 2.7
    from urlparse import urljoin  # noqa


def with_metaclass(meta, *bases):
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
