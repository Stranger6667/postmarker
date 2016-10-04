# coding: utf-8
import pytest

from postmarker.core import ServerClient


class TestClient:

    def test_server_client(self, server_client, api_token, patched_request):
        server_client._call('GET', 'endpoint')
        patched_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Server-Token': api_token, 'Accept': 'application/json'}
        )

    def test_account_client(self, account_client, api_token, patched_request):
        account_client._call('GET', 'endpoint')
        patched_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Account-Token': api_token, 'Accept': 'application/json'}
        )

    def test_no_token(self):
        with pytest.raises(AssertionError) as exc:
            ServerClient()
        assert str(exc.value) == 'You have to provide token to use Postmark API'
