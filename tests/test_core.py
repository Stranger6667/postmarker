# coding: utf-8
import pytest

from postmarker.core import PostmarkClient
from postmarker.exceptions import ConfigError
from postmarker.models.base import ModelManager
from postmarker.models.bounces import BounceManager


class TestClient:

    def test_server_client(self, postmark, api_token, patched_request):
        postmark.call('GET', 'endpoint')
        patched_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Server-Token': api_token, 'Accept': 'application/json'},
            params={}, json=None,
        )

    def test_no_token(self):
        with pytest.raises(AssertionError) as exc:
            PostmarkClient(None)
        assert str(exc.value) == 'You have to provide token to use Postmark API'

    def test_repr(self, postmark, api_token):
        assert repr(postmark) == '<PostmarkClient: %s>' % api_token


class TestManagersSetup:

    def test_duplicate_names(self):
        with pytest.raises(ConfigError) as exc:
            class SuperClient(PostmarkClient):
                _managers = (
                    BounceManager,
                    BounceManager
                )
        assert str(exc.value) == 'Defined managers names are not unique'

    def test_names_overriding(self):

        class BrokenManager(ModelManager):
            name = 'session'

        with pytest.raises(ConfigError) as exc:
            class SuperClient(PostmarkClient):
                _managers = (
                    BrokenManager,
                )
        assert str(exc.value) == "Defined managers names override client's members"
