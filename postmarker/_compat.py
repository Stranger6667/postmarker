# coding: utf-8


try:
    from urllib.parse import urljoin
except ImportError:  # Python 2.7
    from urlparse import urljoin  # noqa


try:
    from unittest.mock import patch
except ImportError:  # Python < 3.3
    try:
        from mock import patch  # noqa
    except ImportError:
        patch = None


try:
    from inspect import signature

    def get_args(cls):
        return list(signature(cls).parameters)


except ImportError:

    def get_args(cls):
        from inspect import getargspec

        return getargspec(cls.__init__).args[1:]
