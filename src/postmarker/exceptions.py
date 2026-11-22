from __future__ import annotations

from typing import Any


class PostmarkerException(Exception):
    """Base class for all exceptions in Postmarker."""


class ClientError(PostmarkerException):
    """Indicates client's error."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.error_code = kwargs.pop("error_code")
        super().__init__(*args, **kwargs)


class TransportError(PostmarkerException):
    """Indicates a request without a usable Postmark response.

    A network failure, a timeout or a body that isn't a Postmark JSON response. The underlying `requests` or `httpx2`
    exception is chained as `__cause__`.
    """

    def __init__(self, *args: Any, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(*args)


class SpamAssassinError(PostmarkerException):
    pass
