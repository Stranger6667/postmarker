import asyncio
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
from unittest.mock import patch

import httpx2
import pytest

from postmarker.core import SPAMCHECK_API, STATUS_API, USER_AGENT, AsyncPostmarkClient
from postmarker.exceptions import ClientError, SpamAssassinError

pytestmark = pytest.mark.anyio


def respond(response=None):
    sent = []

    def handler(request):
        sent.append(request)
        return response or httpx2.Response(200, json={})

    return sent, handler


def make_client(handler, client_class=AsyncPostmarkClient, **kwargs):
    kwargs.setdefault("server_token", "SERVER_TOKEN")
    client = client_class(**kwargs)
    client._transport = httpx2.MockTransport(handler)
    return client


def test_missing_httpx2(monkeypatch):
    monkeypatch.setitem(sys.modules, "httpx2", None)
    with pytest.raises(ImportError, match=r"uv pip install 'postmarker\[async\]'"):
        AsyncPostmarkClient(server_token="SERVER_TOKEN")


def test_core_imports_without_httpx2():
    code = "import sys; sys.modules['httpx2'] = None; import postmarker.core"
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0


async def test_call_encodes_like_requests():
    sent, handler = respond()
    await make_client(handler).call("GET", "endpoint", skipped=None, flag=True, other=False, count=1)
    (request,) = sent
    assert str(request.url).split("?")[0] == "https://api.postmarkapp.com/endpoint"
    assert dict(request.url.params) == {"flag": "True", "other": "False", "count": "1"}
    assert request.headers["X-Postmark-Server-Token"] == "SERVER_TOKEN"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["User-Agent"] == USER_AGENT


async def test_call_keeps_endpoint_query():
    sent, handler = respond()
    await make_client(handler).call("GET", "bounces?type=HardBounce", count=5)
    assert str(sent[0].url) == "https://api.postmarkapp.com/bounces?type=HardBounce&count=5"


async def test_call_sends_json():
    sent, handler = respond()
    await make_client(handler).call("POST", "email", data={"To": "receiver@example.com"})
    (request,) = sent
    assert json.loads(request.content) == {"To": "receiver@example.com"}


async def test_account_token():
    sent, handler = respond()
    client = make_client(handler, server_token=None, account_token="ACCOUNT_TOKEN")
    await client.call("GET", "endpoint", token_type="account")
    (request,) = sent
    assert request.headers["X-Postmark-Account-Token"] == "ACCOUNT_TOKEN"


async def test_account_only_client_server_call():
    sent, handler = respond()
    await make_client(handler, server_token=None, account_token="ACCOUNT_TOKEN").call("GET", "endpoint")
    (request,) = sent
    assert not [name for name in request.headers if name.lower().startswith("x-postmark")]


async def test_client_error():
    _, handler = respond(httpx2.Response(422, json={"ErrorCode": 406, "Message": "Inactive recipient"}))
    with pytest.raises(ClientError, match=r"^\[406\] Inactive recipient$") as exc:
        await make_client(handler).call("GET", "endpoint")
    assert exc.value.error_code == 406


async def test_http_error_without_json():
    _, handler = respond(httpx2.Response(500, text="oops"))
    with pytest.raises(httpx2.HTTPStatusError):
        await make_client(handler).call("GET", "endpoint")


async def test_format_exception_message_overridable():
    class Client(AsyncPostmarkClient):
        def format_exception_message(self, data):
            return "custom"

    _, handler = respond(httpx2.Response(422, json={"ErrorCode": 406, "Message": "Inactive recipient"}))
    with pytest.raises(ClientError, match="^custom$"):
        await make_client(handler, client_class=Client).call("GET", "endpoint")


@pytest.mark.parametrize(
    "timeout, expected",
    (
        (None, {"connect": None, "read": None, "write": None, "pool": None}),
        (5, {"connect": 5, "read": 5, "write": 5, "pool": 5}),
        ((1, 2), {"connect": 1, "read": 2, "write": 2, "pool": 1}),
    ),
)
async def test_timeout(timeout, expected):
    sent, handler = respond()
    await make_client(handler, timeout=timeout).call("GET", "endpoint")
    assert sent[0].extensions["timeout"] == expected


async def test_timeout_read_per_request():
    sent, handler = respond()
    client = make_client(handler)
    client.timeout = 3
    await client.call("GET", "endpoint")
    assert sent[0].extensions["timeout"]["read"] == 3


async def test_follow_redirects():
    def handler(request):
        if request.url.path == "/endpoint":
            return httpx2.Response(302, headers={"Location": "/other"})
        return httpx2.Response(200, json={"ok": 1})

    assert await make_client(handler).call("GET", "endpoint") == {"ok": 1}


def set_proxy(monkeypatch, scheme, url):
    for name in (f"{scheme}_proxy", "no_proxy", "all_proxy"):
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.upper(), raising=False)
    monkeypatch.setenv(f"{scheme}_proxy", url)


def test_retries():
    client = AsyncPostmarkClient(server_token="SERVER_TOKEN", max_retries=3)
    assert client.session._transport._pool._retries == 3


async def test_env_proxy(monkeypatch):
    seen = []

    class Proxy(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    set_proxy(monkeypatch, "http", f"http://127.0.0.1:{server.server_port}")
    try:
        async with AsyncPostmarkClient(server_token="SERVER_TOKEN", root_api_url="http://postmark.invalid/") as client:
            assert await client.call("GET", "server") == {}
    finally:
        server.shutdown()
        server.server_close()
    assert seen == ["http://postmark.invalid/server"]


async def test_concurrent_requests_share_session():
    _, handler = respond()
    client = make_client(handler)
    with patch("httpx2.AsyncClient.__init__", autospec=True, side_effect=httpx2.AsyncClient.__init__) as init:
        results = await asyncio.gather(*(client.call("GET", f"endpoint{i}") for i in range(3)))
    assert results == [{}, {}, {}]
    assert init.call_count == 1


async def test_context_manager_closes():
    _, handler = respond()
    client = make_client(handler)
    async with client as entered:
        await client.call("GET", "endpoint")
        session = client.session
    assert entered is client
    assert session.is_closed


async def test_reuse_after_close():
    _, handler = respond()
    client = make_client(handler)
    async with client:
        await client.call("GET", "endpoint")
    async with client:
        assert await client.call("GET", "endpoint") == {}


def test_from_config():
    client = AsyncPostmarkClient.from_config({"postmark_server_token": "SERVER_TOKEN", "postmark_timeout": 5})
    assert (client.server_token, client.timeout) == ("SERVER_TOKEN", 5)


async def test_logging():
    _, handler = respond()
    stream = StringIO()
    await make_client(handler, verbosity=2, logs_stream=stream).call("GET", "endpoint")
    assert "Request: GET https://api.postmarkapp.com/endpoint" in stream.getvalue()
    assert "Response: {}" in stream.getvalue()


async def test_spamcheck_error():
    sent, handler = respond(httpx2.Response(200, json={"success": False, "message": "bad"}))
    with pytest.raises(SpamAssassinError, match="^bad$"):
        await make_client(handler).spamcheck("dump")
    assert str(sent[0].url) == SPAMCHECK_API
    assert json.loads(sent[0].content) == {"email": "dump", "options": "long"}


async def test_spamcheck():
    _, handler = respond(httpx2.Response(200, json={"success": True, "score": "1"}))
    assert await make_client(handler).spamcheck("dump", options="short") == {"success": True, "score": "1"}


async def test_call_status():
    sent, handler = respond(httpx2.Response(200, json=[]))
    assert await make_client(handler).call_status("services") == []
    assert str(sent[0].url) == STATUS_API + "services"


async def test_aclose_without_requests():
    client = AsyncPostmarkClient(server_token="SERVER_TOKEN")
    await client.aclose()
    # Closing must not open a connection pool just to close it
    assert not hasattr(client, "_session")
