# coding: utf-8
import pytest

from postmarker.core import BaseClient, ServerClient
from postmarker.exceptions import ConfigError
from postmarker.models.base import ModelManager
from postmarker.models.bounces import BounceManager


class TestClient:

    def test_server_client(self, server_client, api_token, patched_request):
        server_client._call('GET', 'endpoint')
        patched_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Server-Token': api_token, 'Accept': 'application/json'},
            params={}, json=None,
        )

    def test_account_client(self, account_client, api_token, patched_request):
        account_client._call('GET', 'endpoint')
        patched_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Account-Token': api_token, 'Accept': 'application/json'},
            params={}, json=None,
        )

    def test_no_token(self):
        with pytest.raises(AssertionError) as exc:
            ServerClient()
        assert str(exc.value) == 'You have to provide token to use Postmark API'

    def test_repr(self, server_client, api_token):
        assert repr(server_client) == '<ServerClient: %s>' % api_token


class TestManagersSetup:

    def test_duplicate_names(self):
        with pytest.raises(ConfigError) as exc:
            class SuperClient(BaseClient):
                _managers = (
                    BounceManager,
                    BounceManager
                )
        assert str(exc.value) == 'Defined managers names are not unique'

    def test_names_overriding(self):

        class BrokenManager(ModelManager):
            name = 'session'

        with pytest.raises(ConfigError) as exc:
            class SuperClient(BaseClient):
                _managers = (
                    BrokenManager,
                )
        assert str(exc.value) == "Defined managers names override client's members"
