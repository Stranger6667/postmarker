from __future__ import annotations

from typing import Any


class PostmarkerException(Exception):
    """Base class for all exceptions in Postmarker."""


class ClientError(PostmarkerException):
    """Indicates client's error."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.error_code = kwargs.pop("error_code")
        super().__init__(*args, **kwargs)


class SpamAssassinError(PostmarkerException):
    pass
