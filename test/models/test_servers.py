from unittest.mock import call

import pytest

from postmarker.core import USER_AGENT
from postmarker.models.servers import AccountServer

HEADERS = {
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
    "X-Postmark-Account-Token": "ACCOUNT_TOKEN",
}
# Examples from https://postmarkapp.com/developer/api/servers-api
STAGING = {
    "ID": 1,
    "Name": "Staging Testing",
    "ApiTokens": ["server token"],
    "Color": "red",
    "SmtpApiActivated": True,
    "RawEmailEnabled": False,
    "DeliveryType": "Live",
    "ServerLink": "https://postmarkapp.com/servers/1/streams",
    "InboundAddress": "yourhash@inbound.postmarkapp.com",
    "InboundHookUrl": "https://hooks.example.com/inbound",
    "BounceHookUrl": "https://hooks.example.com/bounce",
    "OpenHookUrl": "https://hooks.example.com/open",
    "DeliveryHookUrl": "https://hooks.example.com/delivery",
    "PostFirstOpenOnly": False,
    "InboundDomain": "",
    "InboundHash": "yourhash",
    "InboundSpamThreshold": 5,
    "TrackOpens": False,
    "TrackLinks": "None",
    "IncludeBounceContentInHook": True,
    "ClickHookUrl": "https://hooks.example.com/click",
    "EnableSmtpApiErrorHooks": False,
}
PRODUCTION = {**STAGING, "Name": "Production Testing", "Color": "blue", "SmtpApiActivated": False}
SANDBOX = {
    **STAGING,
    "ID": 2,
    "Name": "Production02",
    "Color": "green",
    "DeliveryType": "Sandbox",
    "ServerLink": "https://postmarkapp.com/servers/2/streams",
}
DELETED = {"ErrorCode": 0, "Message": "Server Production Server 2 removed."}


def request(method, endpoint, json=None, params=None):
    return call(
        method,
        f"https://api.postmarkapp.com{endpoint}",
        json=json,
        params=params or {},
        headers=HEADERS,
        timeout=None,
    )


@pytest.fixture
def server(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = STAGING
    instance = postmark_client.servers.get(1)
    postmark_request.reset_mock()
    return instance


class TestManager:
    def test_all(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = {"TotalCount": 2, "Servers": [STAGING, SANDBOX]}
        servers = postmark_client.servers.all()
        assert postmark_request.call_args_list == [
            request("GET", "/servers", params={"count": 500, "offset": 0, "name": None})
        ]
        assert all(isinstance(server, AccountServer) for server in servers)
        assert [server.as_dict() for server in servers] == [STAGING, SANDBOX]

    def test_all_name(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = {"TotalCount": 1, "Servers": [STAGING]}
        servers = postmark_client.servers.all(count=10, offset=5, name="Staging")
        assert postmark_request.call_args_list == [
            request("GET", "/servers", params={"count": 10, "offset": 5, "name": "Staging"})
        ]
        assert [server.as_dict() for server in servers] == [STAGING]

    def test_all_paginates(self, postmark_client, postmark_request):
        postmark_request.return_value.json.side_effect = [
            {"TotalCount": 600, "Servers": [STAGING]},
            {"TotalCount": 600, "Servers": [SANDBOX]},
        ]
        servers = postmark_client.servers.all(count=600)
        assert postmark_request.call_args_list == [
            request("GET", "/servers", params={"count": 500, "offset": 0, "name": None}),
            request("GET", "/servers", params={"count": 100, "offset": 500, "name": None}),
        ]
        assert [server.as_dict() for server in servers] == [STAGING, SANDBOX]

    def test_get(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = STAGING
        server = postmark_client.servers.get(1)
        assert postmark_request.call_args_list == [request("GET", "/servers/1")]
        assert isinstance(server, AccountServer)
        assert server.as_dict() == STAGING

    def test_create(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = STAGING
        server = postmark_client.servers.create("Staging Testing", Color="Red", InboundSpamThreshold=5)
        assert postmark_request.call_args_list == [
            request("POST", "/servers", json={"Name": "Staging Testing", "Color": "Red", "InboundSpamThreshold": 5})
        ]
        assert isinstance(server, AccountServer)
        assert server.as_dict() == STAGING

    def test_edit(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = PRODUCTION
        assert postmark_client.servers.edit(1, Name="Production Testing", Color="Blue") == PRODUCTION
        assert postmark_request.call_args_list == [
            request("PUT", "/servers/1", json={"Name": "Production Testing", "Color": "Blue"})
        ]

    def test_delete(self, postmark_client, postmark_request):
        postmark_request.return_value.json.return_value = DELETED
        assert postmark_client.servers.delete(2) == "Server Production Server 2 removed."
        assert postmark_request.call_args_list == [request("DELETE", "/servers/2")]


class TestModel:
    def test_str(self, server):
        assert str(server) == "AccountServer: Staging Testing (1)"

    def test_get(self, server, postmark_request):
        postmark_request.return_value.json.return_value = PRODUCTION
        assert server.get() is server
        assert postmark_request.call_args_list == [request("GET", "/servers/1")]
        assert server.as_dict() == PRODUCTION
        assert server.Name == "Production Testing"

    def test_edit(self, server, postmark_request):
        postmark_request.return_value.json.return_value = PRODUCTION
        server.edit(Name="Production Testing", Color="Blue")
        assert postmark_request.call_args_list == [
            request("PUT", "/servers/1", json={"Name": "Production Testing", "Color": "Blue"})
        ]
        assert server.as_dict() == PRODUCTION
        assert server.Name == "Production Testing"

    def test_delete(self, server, postmark_request):
        postmark_request.return_value.json.return_value = DELETED
        assert server.delete() == "Server Production Server 2 removed."
        assert postmark_request.call_args_list == [request("DELETE", "/servers/1")]
