# coding: utf-8


try:
    from urllib.parse import urljoin
except ImportError:  # Python 2.7
    from urlparse import urljoin  # noqa
