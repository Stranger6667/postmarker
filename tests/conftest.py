# coding: utf-8
import pytest

from postmarker.core import AccountClient, ServerClient

from ._compat import patch


API_TOKEN = 'POSTMARK_API_TEST'


@pytest.fixture
def api_token():
    return API_TOKEN


@pytest.fixture
def server_client(api_token):
    return ServerClient(token=api_token)


@pytest.fixture
def account_client(api_token):
    return AccountClient(token=api_token)


@pytest.yield_fixture
def patched_request():
    """
    Mocks network requests.
    """
    with patch('postmarker.core.requests.request') as patched:
        yield patched
