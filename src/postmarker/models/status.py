from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import AsyncModelManager, Model, ModelManager

if TYPE_CHECKING:
    from ..core import AsyncPostmarkClient, PostmarkClient


class Incident(Model):
    def __str__(self) -> str:
        return "{}: {}".format(self.__class__.__name__, self._data.get("id"))


class IncidentsManager(ModelManager[Incident]):
    name = "incidents"
    model = Incident

    def call(self, *args: Any, **kwargs: Any) -> Any:
        return self.client.call_status(*args, **kwargs)

    @property
    def last(self) -> Incident:
        return self._init_instance(self.call("last_incident"))

    def all(self) -> list[Incident]:
        return self._init_many(self.call("incidents"))

    def get(self, id: int) -> Incident:
        return self._init_instance(self.call(f"incidents/{id}"))


class StatusManager(ModelManager[Model]):
    """Gathers logic about Postmark systems status."""

    name = "status"

    def __init__(self, client: PostmarkClient) -> None:
        super().__init__(client)
        self.incidents = IncidentsManager(self.client)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        return self.client.call_status(*args, **kwargs)

    def get(self) -> Any:
        return self.call("status")

    @property
    def services(self) -> Any:
        return self.call("services")

    @property
    def availability(self) -> Any:
        return self.call("services/availability")

    @property
    def delivery(self) -> Any:
        return self.call("delivery")


class AsyncIncidentsManager(AsyncModelManager[Incident]):
    """Async twin of :py:class:`IncidentsManager`."""

    name = "incidents"
    model = Incident

    async def call(self, *args: Any, **kwargs: Any) -> Any:
        return await self.client.call_status(*args, **kwargs)

    @property
    async def last(self) -> Incident:
        return self._init_instance(await self.call("last_incident"))

    async def all(self) -> list[Incident]:
        return self._init_many(await self.call("incidents"))

    async def get(self, id: int) -> Incident:
        return self._init_instance(await self.call(f"incidents/{id}"))


class AsyncStatusManager(AsyncModelManager[Model]):
    """Async twin of :py:class:`StatusManager`."""

    name = "status"

    def __init__(self, client: AsyncPostmarkClient) -> None:
        super().__init__(client)
        self.incidents = AsyncIncidentsManager(self.client)

    async def call(self, *args: Any, **kwargs: Any) -> Any:
        return await self.client.call_status(*args, **kwargs)

    async def get(self) -> Any:
        return await self.call("status")

    @property
    async def services(self) -> Any:
        return await self.call("services")

    @property
    async def availability(self) -> Any:
        return await self.call("services/availability")

    @property
    async def delivery(self) -> Any:
        return await self.call("delivery")
