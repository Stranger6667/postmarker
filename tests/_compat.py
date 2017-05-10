# coding: utf-8


try:
    from unittest.mock import patch, Mock
except ImportError:  # Python < 3.3
    from mock import patch, Mock  # noqa
