# coding: utf-8


try:
    from unittest.mock import Mock, patch
except ImportError:  # Python < 3.3
    from mock import Mock, patch  # noqa
