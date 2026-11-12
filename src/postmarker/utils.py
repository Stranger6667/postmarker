from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from inspect import signature
from typing import Any, TypeVar

T = TypeVar("T")


def chunks(container: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    """Split a container into n-sized chunks."""
    for i in range(0, len(container), n):
        yield container[i : i + n]


def sizes(count: int | None, offset: int = 0, max_chunk: int = 500) -> Iterator[tuple[int, int]]:
    """Helper to iterate over remote data via count & offset pagination."""
    if count is None:
        chunk = max_chunk
        while True:
            yield chunk, offset
            offset += chunk
    else:
        while count:
            chunk = min(count, max_chunk)
            count = max(0, count - max_chunk)
            yield chunk, offset
            offset += chunk


def get_args(cls: Callable[..., Any]) -> list[str]:
    return list(signature(cls).parameters)
