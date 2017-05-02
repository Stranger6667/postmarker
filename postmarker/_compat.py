# coding: utf-8


try:
    from urllib.parse import urljoin
except ImportError:  # Python 2.7
    from urlparse import urljoin  # noqa

try:
    from inspect import signature

    def get_args(cls):
        return list(signature(cls).parameters)

except ImportError:
    from inspect import getargspec

    def get_args(cls):
        return getargspec(cls.__init__).args[1:]
