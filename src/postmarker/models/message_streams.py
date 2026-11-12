from __future__ import annotations

from typing import Any

from .base import Model, ModelManager


class MessageStream(Model):
    def get(self) -> MessageStream:
        self._update(self._manager.get(self.ID).as_dict())
        return self

    def edit(self, **kwargs: Any) -> None:
        self._update(self._manager.edit(self.ID, **kwargs).as_dict())

    def archive(self) -> Any:
        return self._manager.archive(self.ID)

    def unarchive(self) -> MessageStream:
        restored: MessageStream = self._manager.unarchive(self.ID)
        return restored


class MessageStreamsManager(ModelManager[MessageStream]):
    name = "message_streams"
    model = MessageStream

    def all(
        self, MessageStreamType: str | None = None, IncludeArchivedStreams: bool | None = None
    ) -> list[MessageStream]:
        """Lists the server's message streams.

        :param MessageStreamType: ``All`` (default), ``Inbound``, ``Transactional`` or ``Broadcasts``.
        :param IncludeArchivedStreams: Include archived streams; ``False`` by default.
        """
        response = self.call(
            "GET",
            "/message-streams",
            MessageStreamType=MessageStreamType,
            IncludeArchivedStreams=IncludeArchivedStreams,
        )
        return self._init_many(response["MessageStreams"])

    def get(self, id: str) -> MessageStream:
        return self._init_instance(self.call("GET", f"/message-streams/{id}"))

    def create(
        self,
        ID: str,
        Name: str,
        MessageStreamType: str,
        Description: str | None = None,
        SubscriptionManagementConfiguration: dict[str, Any] | None = None,
    ) -> MessageStream:
        """Creates a message stream.

        :param ID: Stream ID to send messages with, e.g. ``transactional-dev``.
        :param MessageStreamType: ``Broadcasts`` or ``Transactional``.
        :param SubscriptionManagementConfiguration: E.g. ``{"UnsubscribeHandlingType": "Postmark"}``.
        """
        data = {
            "ID": ID,
            "Name": Name,
            "MessageStreamType": MessageStreamType,
            "Description": Description,
            "SubscriptionManagementConfiguration": SubscriptionManagementConfiguration,
        }
        return self._init_instance(self.call("POST", "/message-streams", data=_without_none(data)))

    def edit(
        self,
        id: str,
        Name: str | None = None,
        Description: str | None = None,
        SubscriptionManagementConfiguration: dict[str, Any] | None = None,
    ) -> MessageStream:
        """Updates the given fields of a message stream; omitted fields stay unchanged."""
        data = {
            "Name": Name,
            "Description": Description,
            "SubscriptionManagementConfiguration": SubscriptionManagementConfiguration,
        }
        return self._init_instance(self.call("PATCH", f"/message-streams/{id}", data=_without_none(data)))

    def archive(self, id: str) -> Any:
        """Archives a message stream. Postmark deletes it after ``ExpectedPurgeDate`` from the response."""
        return self.call("POST", f"/message-streams/{id}/archive")

    def unarchive(self, id: str) -> MessageStream:
        """Restores an archived message stream before its ``ExpectedPurgeDate``."""
        return self._init_instance(self.call("POST", f"/message-streams/{id}/unarchive"))


def _without_none(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}
