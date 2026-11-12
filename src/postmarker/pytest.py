from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import DEFAULT, MagicMock, patch

import pytest
import requests

from .core import PostmarkClient


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
