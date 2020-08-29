from unittest.mock import patch

import pytest

from .core import PostmarkClient, requests


@pytest.yield_fixture
def postmark_request():
    """Mocks network requests to Postmark API."""
    if patch is None:
        raise AssertionError('To use pytest fixtures on Python 2, please, install postmarker["tests"]')
    with patch("postmarker.core.requests.Session.request", wraps=requests.Session().request) as patched:
        with patch("postmarker.core.requests.Session.send"):
            yield patched


@pytest.yield_fixture
def postmark_client(postmark_request):  # pylint: disable=redefined-outer-name
    client = PostmarkClient(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")
    client.mock = postmark_request
    yield client
