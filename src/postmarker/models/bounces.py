"""Bounces.

Information about bounces is available via the :py:class:`~postmarker.models.bounces.BounceManager`,
which is an attribute of ``postmark`` instance.
"""

from __future__ import annotations

from typing import Any

from .base import MessageModel, ModelManager


class Bounce(MessageModel):
    """Bounce model."""

    @property
    def dump(self) -> Any:
        """Gets SMTP data dump.

        :return: Dump of SMTP data if it is available.
        :rtype: `str` or `None`
        """
        return self._manager.get_dump(self.ID)

    def activate(self) -> Any:
        """Activates the bounce instance and updates it with the latest data.

        :return: Activation status.
        :rtype: `str`
        """
        response = self._manager.activate(self.ID)
        self._update(response["Bounce"])
        return response["Message"]


class BounceManager(ModelManager[Bounce]):
    """Encapsulates logic about bounces."""

    name = "bounces"
    model = Bounce

    @property
    def deliverystats(self) -> Any:
        """Returns number of inactive emails and list of bounce types with total counts.

        :rtype: `dict`
        """
        return self.call("GET", "/deliverystats")

    @property
    def tags(self) -> Any:
        """A list of tags that have generated bounces for a given server.

        :rtype: `list`
        """
        return self.call("GET", "/bounces/tags")

    def get(self, id: int) -> Bounce:
        """Returns a single bounce.

        :param int id: Bounce ID.
        :rtype: :py:class:`Bounce`
        """
        response = self.call("GET", f"/bounces/{id}")
        return self._init_instance(response)

    def all(
        self,
        count: int | None = 500,
        offset: int = 0,
        type: str | None = None,
        inactive: bool | None = None,
        emailFilter: str | None = None,
        tag: str | None = None,
        messageID: str | None = None,
        fromdate: Any = None,
        todate: Any = None,
    ) -> list[Bounce]:
        """Returns many bounces.

        :param int count: Number of bounces to return per request.
        :param int offset: Number of bounces to skip.
        :param str type: Filter by type of bounce.
        :param bool inactive: Filter by emails that were deactivated by Postmark due to the bounce.
        :param str emailFilter: Filter by email address.
        :param str tag: Filter by tag.
        :param str messageID: Filter by messageID.
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :param date todate: Filter messages up to the date specified (inclusive).
        :return: A list of :py:class:`Bounce` instances.
        :rtype: `list`
        """
        responses = self.call_many(
            "GET",
            "/bounces/",
            count=count,
            offset=offset,
            type=type,
            inactive=inactive,
            emailFilter=emailFilter,
            tag=tag,
            messageID=messageID,
            fromdate=fromdate,
            todate=todate,
        )
        return self.expand_responses(responses, "Bounces")

    def activate(self, id: int) -> Any:
        """Activates a bounce.

        :param int id: Bounce ID.
        :return: Activation result and bounce data.
        :rtype: `dict`
        """
        return self.call("PUT", f"/bounces/{id}/activate")

    def get_dump(self, id: int) -> Any:
        """Gets an SMTP data dump.

        :param int id: Bounce ID.
        :return: A dump of SMTP data if it is available.
        :rtype: `str` or `None`
        """
        return self.call("GET", f"/bounces/{id}/dump").get("Body")

    def Bounce(self, json: str | bytes) -> Bounce:
        """Constructs new Bounce instance from JSON-encoded string. Intended to use for bounce webhook processing.

        :param json: `str`
        :return: :py:class:`Bounce`
        """
        return self.model.from_json(json, manager=self)
