from __future__ import annotations

from collections.abc import Iterator
from json import loads
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ..utils import sizes

if TYPE_CHECKING:
    from ..core import PostmarkClient

ModelT = TypeVar("ModelT", bound="Model")


class Model:
    """Abstract data model for Postmark entities."""

    _data: dict[str, Any]
    _manager: Any

    def __init__(self, manager: Any = None, **kwargs: Any) -> None:
        self._manager = manager
        self._data = {}
        self._update(kwargs)

    if TYPE_CHECKING:
        # Postmark fields are set as instance attributes, as is
        def __getattr__(self, name: str) -> Any: ...

    def __str__(self) -> str:
        return "{}: {}".format(self.__class__.__name__, self._data.get("ID"))

    def __repr__(self) -> str:
        return f"<{self}>"

    def _update(self, kwargs: dict[str, Any]) -> None:
        self._data.update(kwargs)
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls: type[ModelT], json: str | bytes, manager: Any = None) -> ModelT:
        data = loads(json)
        return cls(manager=manager, **data)

    def as_dict(self) -> dict[str, Any]:
        return self._data.copy()


class ModelManager(Generic[ModelT]):
    """Proxies calls to main API client. Encapsulates logic of certain part of API - bounces, emails, etc."""

    name: str
    model: type[ModelT]
    token_type = "server"
    count_key = "count"
    offset_key = "offset"
    max_chunk_size = 500
    # Upper bound for count + offset; Postmark search endpoints reject anything above 10,000
    pagination_limit: int | None = None

    def __init__(self, client: PostmarkClient) -> None:
        self.client = client

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self}>"

    def _init_instance(self, data: dict[str, Any]) -> ModelT:
        return self.model(manager=self, **data)

    def _init_many(self, data: list[dict[str, Any]]) -> list[ModelT]:
        return [self._init_instance(part) for part in data]

    def call(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["token_type"] = self.token_type
        return self.client.call(*args, **kwargs)

    def call_many(self, *args: Any, **kwargs: Any) -> list[Any]:
        return list(self._call_many(*args, **kwargs))

    def _call_many(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        count = kwargs.pop(self.count_key)
        offset = kwargs.pop(self.offset_key)
        if self.pagination_limit is not None:
            reachable = max(0, self.pagination_limit - offset)
            count = reachable if count is None else min(count, reachable)
        loaded_items_count = 0
        for _count, _offset in sizes(count, offset, self.max_chunk_size):
            response = self.call(*args, **self.update_kwargs(kwargs, _count, _offset))
            loaded_items_count += _count
            yield response
            # We expect, that we will load `TotalCount` - offset items.
            # This number will be less or equal to number of already loaded items.
            # It could be less in case if latest response contains less items than provided `count` value.
            if response["TotalCount"] - offset <= loaded_items_count:
                break

    def expand_responses(self, responses: list[Any], key: str) -> list[ModelT]:
        return [item for response in responses for item in self._init_many(response[key])]

    def update_kwargs(self, kwargs: dict[str, Any], count: int, offset: int) -> dict[str, Any]:
        """Helper to support handy dictionaries merging on all Python versions."""
        kwargs.update({self.count_key: count, self.offset_key: offset})
        return kwargs


class SubModelManager(ModelManager[ModelT]):
    """Works with multiple model managers.

    Example:
        >>> postmark = PostmarkClient(server_token='TEST')
        >>> postmark.messages.outbound.all()
        []

    """

    _managers: tuple[type[ModelManager[Any]], ...] = ()

    def __init__(self, client: PostmarkClient) -> None:
        super().__init__(client)
        self._setup_managers()

    def _setup_managers(self) -> None:
        for manager_class in self._managers:
            instance = manager_class(self.client)
            setattr(self, instance.name, instance)


class MessageModel(Model):
    @property
    def message(self) -> Any:
        return self._manager.client.messages.outbound.get(self.MessageID)
