from unittest.mock import patch

import pytest
from requests import ConnectTimeout, HTTPError, Response

from postmarker.core import DEFAULT_TIMEOUT, USER_AGENT, PostmarkClient
from postmarker.exceptions import TransportError
from postmarker.models.messages import MessageManager, OutboundMessageManager
from postmarker.models.triggers import TriggersManager


def test_server_client(postmark, server_token, postmark_request):
    postmark.call("GET", "endpoint")
    postmark_request.assert_called_with(
        "GET",
        "https://api.postmarkapp.com/endpoint",
        headers={
            "X-Postmark-Server-Token": server_token,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        params={},
        json=None,
        timeout=30,
    )


def test_account_client(postmark_request):
    postmark = PostmarkClient(account_token="ACCOUNT_TOKEN")
    postmark.call("GET", "endpoint", token_type="account")
    postmark_request.assert_called_with(
        "GET",
        "https://api.postmarkapp.com/endpoint",
        headers={
            "X-Postmark-Account-Token": "ACCOUNT_TOKEN",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        params={},
        json=None,
        timeout=30,
    )


def test_account_client_server_call():
    # Without a server token, server calls go without any token header and Postmark rejects them
    postmark = PostmarkClient(account_token="ACCOUNT_TOKEN")
    with patch("postmarker.core.requests.Session.send") as send:
        postmark.call("GET", "endpoint")
    prepared = send.call_args[0][0]
    assert {name: value for name, value in prepared.headers.items() if name.startswith("X-Postmark")} == {}


@pytest.mark.parametrize("kwargs", ({}, {"server_token": None, "account_token": None}))
def test_client_no_token(kwargs):
    with pytest.raises(AssertionError) as exc:
        PostmarkClient(**kwargs)
    # Pytest rewrites asserts in its plugins' packages, postmarker included, and appends the explanation
    assert str(exc.value).splitlines()[0] == "You have to provide server_token or account_token to use Postmark API"


def test_client_repr(postmark, server_token):
    assert repr(postmark) == f"<PostmarkClient: {server_token}>"


@pytest.mark.parametrize(
    "config, kwargs",
    (
        (
            {"POSTMARK_SERVER_TOKEN": "foo", "POSTMARK_TIMEOUT": 1},
            {"is_uppercase": True},
        ),
        (
            {"postmark_server_token": "foo", "postmark_timeout": 1},
            {"is_uppercase": False},
        ),
    ),
)
def test_client_from_config(config, kwargs):
    instance = PostmarkClient.from_config(config, **kwargs)
    assert instance.server_token == "foo"
    assert instance.timeout == 1
    assert instance.account_token is None


WITH_MANAGERS = (PostmarkClient, OutboundMessageManager, MessageManager, TriggersManager)


@pytest.mark.parametrize("klass", WITH_MANAGERS)
def test_managers_duplicate_names(klass):
    managers_names = [manager.name for manager in klass._managers]
    assert len(managers_names) == len(set(managers_names)), "Defined managers names are not unique"


@pytest.mark.parametrize("klass", WITH_MANAGERS)
def test_managers_names_overriding(klass):
    assert not any(manager.name in dir(klass) for manager in klass._managers), (
        "Defined managers names override client's members"
    )


def test_default_timeout(postmark, postmark_request):
    postmark.call("GET", "endpoint")
    assert postmark_request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT == 30


def make_response(status_code, content):
    response = Response()
    response.status_code = status_code
    response._content = content
    return response


@pytest.mark.parametrize(
    "status_code, content",
    [
        (500, b"Server Error"),
        (502, b'{"error": "Bad Gateway"}'),
        (200, b"<html>OK</html>"),
    ],
    ids=["http-error-without-json", "json-without-error-code", "success-without-json"],
)
def test_transport_error_for_unusable_response(postmark, postmark_request, status_code, content):
    postmark_request.return_value = make_response(status_code, content)
    with pytest.raises(TransportError) as exc:
        postmark.call("GET", "endpoint")
    assert exc.value.status_code == status_code


def test_transport_error_keeps_http_error_as_cause(postmark, postmark_request):
    postmark_request.return_value = make_response(500, b"Server Error")
    with pytest.raises(TransportError, match="Server Error") as exc:
        postmark.call("GET", "endpoint")
    assert isinstance(exc.value.__cause__, HTTPError)


def test_transport_error_for_network_failure(postmark, postmark_request):
    postmark_request.side_effect = ConnectTimeout("timed out")
    with pytest.raises(TransportError, match="timed out") as exc:
        postmark.call("GET", "endpoint")
    assert exc.value.status_code is None
    assert isinstance(exc.value.__cause__, ConnectTimeout)


def test_model_manager_import_path():
    # Importable from `postmarker.core` before the async client; kept for existing imports
    from postmarker.core import ModelManager
    from postmarker.models.base import ModelManager as BaseModuleModelManager

    assert ModelManager is BaseModuleModelManager
