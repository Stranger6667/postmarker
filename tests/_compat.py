# coding: utf-8


try:
    from unittest.mock import patch
except ImportError:  # Python 2.7
    from mock import patch  # noqa
