# coding: utf-8
from __future__ import absolute_import

import pytest

from ._compat import patch
from .core import PostmarkClient


@pytest.yield_fixture
def postmark_request():
    """
    Mocks network requests to Postmark API.
    """
    with patch('postmarker.core.requests.Session.request') as patched:
        yield patched


@pytest.yield_fixture
def postmark_client(postmark_request):
    client = PostmarkClient(server_token='SERVER_TOKEN', account_token='ACCOUNT_TOKEN')
    client.mock = postmark_request
    yield client
