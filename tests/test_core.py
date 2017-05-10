# coding: utf-8
import pytest

from postmarker.core import USER_AGENT, PostmarkClient
from postmarker.models.messages import MessageManager, OutboundMessageManager
from postmarker.models.triggers import TriggersManager


class TestClient:

    def test_server_client(self, postmark, server_token, postmark_request):
        postmark.call('GET', 'endpoint')
        postmark_request.assert_called_with(
            'GET',
            'https://api.postmarkapp.com/endpoint',
            headers={'X-Postmark-Server-Token': server_token, 'Accept': 'application/json', 'User-Agent': USER_AGENT},
            params={}, json=None, timeout=None
        )

    def test_no_token(self):
        with pytest.raises(AssertionError) as exc:
            PostmarkClient(None)
        assert exc.match('You have to provide token to use Postmark API')

    def test_repr(self, postmark, server_token):
        assert repr(postmark) == '<PostmarkClient: %s>' % server_token


@pytest.mark.parametrize('klass', (PostmarkClient, OutboundMessageManager, MessageManager, TriggersManager))
class TestManagersSetup:

    def test_duplicate_names(self, klass):
        managers_names = [manager.name for manager in klass._managers]
        assert len(managers_names) == len(set(managers_names)), 'Defined managers names are not unique'

    def test_names_overriding(self, klass):
        assert not any(manager.name in dir(klass) for manager in klass._managers), \
            "Defined managers names override client's members"
