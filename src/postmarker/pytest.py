from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import pytest
import requests

from .core import AsyncPostmarkClient, PostmarkClient


@pytest.fixture
def postmark_request() -> Iterator[MagicMock]:
    """Mocks network requests to Postmark API."""
    prepare = requests.Session().request

    def side_effect(*args: Any, **kwargs: Any) -> Any:
        # Real request preparation (payload serialization) with the mocked `send`
        prepare(*args, **kwargs)
        return DEFAULT

    with (
        patch("postmarker.core.requests.Session.request", side_effect=side_effect) as patched,
        patch("postmarker.core.requests.Session.send"),
    ):
        yield patched


@pytest.fixture
def postmark_client(postmark_request: MagicMock) -> Iterator[PostmarkClient]:
    client = PostmarkClient(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")
    client.mock = postmark_request  # type: ignore[attr-defined]
    yield client


@pytest.fixture
def postmark_async_request() -> Iterator[AsyncMock]:
    """Mocks network requests of `AsyncPostmarkClient` to Postmark API."""
    import httpx2

    def side_effect(method: str, url: str, *, json: Any, **kwargs: Any) -> Any:
        # Real payload serialization with the mocked network call
        httpx2.Request(method, url, json=json)
        return DEFAULT

    with patch.object(
        AsyncPostmarkClient, "_request", new_callable=AsyncMock, side_effect=side_effect, return_value=MagicMock()
    ) as patched:
        yield patched


@pytest.fixture
def postmark_async_client(postmark_async_request: AsyncMock) -> Iterator[AsyncPostmarkClient]:
    client = AsyncPostmarkClient(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")
    client.mock = postmark_async_request  # type: ignore[attr-defined]
    yield client
