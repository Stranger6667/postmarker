from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Model, ModelManager

if TYPE_CHECKING:
    from ..core import PostmarkClient


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
