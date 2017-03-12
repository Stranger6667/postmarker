# coding: utf-8


try:
    from unittest.mock import patch, Mock
except ImportError:  # Python 2.7
    from mock import patch, Mock  # noqa
