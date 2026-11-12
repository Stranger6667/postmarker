from unittest.mock import DEFAULT, patch

import pytest

from .core import PostmarkClient, requests


@pytest.fixture
def postmark_request():
    """Mocks network requests to Postmark API."""
    prepare = requests.Session().request

    def side_effect(*args, **kwargs):
        # Real request preparation (payload serialization) with the mocked `send`
        prepare(*args, **kwargs)
        return DEFAULT

    with (
        patch("postmarker.core.requests.Session.request", side_effect=side_effect) as patched,
        patch("postmarker.core.requests.Session.send"),
    ):
        yield patched


@pytest.fixture
def postmark_client(postmark_request):
    client = PostmarkClient(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")
    client.mock = postmark_request
    yield client
