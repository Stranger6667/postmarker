import subprocess
import sys

import pytest

from postmarker.core import USER_AGENT, AsyncPostmarkClient, PostmarkClient

pytestmark = pytest.mark.anyio


def test_postmark_client(postmark_client, postmark_request):
    assert isinstance(postmark_client, PostmarkClient)
    assert postmark_client.mock is postmark_request


def test_return_value_configurable(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {"ID": 1}
    assert postmark_client.call("GET", "/server") == {"ID": 1}


def test_payload_still_serialized(postmark_client):
    with pytest.raises(Exception, match="not JSON serializable"):
        postmark_client.call("POST", "/email", data={"Metadata": object()})


async def test_postmark_async_client(postmark_async_client, postmark_async_request):
    assert isinstance(postmark_async_client, AsyncPostmarkClient)
    assert postmark_async_client.mock is postmark_async_request


async def test_async_call_args_match_sync_shape(postmark_async_client, postmark_async_request):
    await postmark_async_client.call("GET", "endpoint")
    postmark_async_request.assert_called_with(
        "GET",
        "https://api.postmarkapp.com/endpoint",
        headers={"X-Postmark-Server-Token": "SERVER_TOKEN", "Accept": "application/json", "User-Agent": USER_AGENT},
        params={},
        json=None,
        timeout=30,
    )


async def test_async_return_value_configurable(postmark_async_client, postmark_async_request):
    postmark_async_request.return_value.json.return_value = {"ID": 1}
    assert await postmark_async_client.call("GET", "/server") == {"ID": 1}


async def test_async_payload_still_serialized(postmark_async_client):
    with pytest.raises(Exception, match="not JSON serializable"):
        await postmark_async_client.call("POST", "/email", data={"Metadata": object()})


def test_plugin_imports_without_httpx2():
    code = "import sys; sys.modules['httpx2'] = None; import postmarker.pytest"
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0
