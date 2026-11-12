"""Suppressions.

Suppressed addresses of a message stream are available via the
:py:class:`~postmarker.models.suppressions.SuppressionsManager`, which is an attribute of ``postmark`` instance.
"""

from __future__ import annotations

from typing import Any

from .base import MessageModel, Model, ModelManager

DEFAULT_STREAM_ID = "outbound"


class Suppression(Model):
    """Suppression model."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.EmailAddress}"


class SubscriptionChange(MessageModel):
    """Subscription change webhook model: an address added to or removed from a suppression list."""

    def __str__(self) -> str:
        return "Subscription change for {}".format(self._data.get("Recipient"))


class SuppressionsManager(ModelManager[Suppression]):
    """Encapsulates logic about suppressions."""

    name = "suppressions"
    model = Suppression

    def all(
        self,
        stream_id: str = DEFAULT_STREAM_ID,
        SuppressionReason: str | None = None,
        Origin: str | None = None,
        fromdate: Any = None,
        todate: Any = None,
        EmailAddress: str | None = None,
    ) -> list[Suppression]:
        """Returns suppressed addresses of a message stream.

        :param str stream_id: Message stream ID.
        :param str SuppressionReason: `HardBounce`, `SpamComplaint` or `ManualSuppression`.
        :param str Origin: `Recipient`, `Customer` or `Admin`.
        :param fromdate: Suppressed on or after this date.
        :param todate: Suppressed on or before this date.
        :param str EmailAddress: Email address.
        :rtype: `list` of :py:class:`Suppression`
        """
        response = self.call(
            "GET",
            f"/message-streams/{stream_id}/suppressions/dump",
            SuppressionReason=SuppressionReason,
            Origin=Origin,
            fromdate=fromdate,
            todate=todate,
            EmailAddress=EmailAddress,
        )
        return self._init_many(response["Suppressions"])

    def create(self, emails: list[str], stream_id: str = DEFAULT_STREAM_ID) -> list[dict[str, Any]]:
        """Suppresses up to 50 addresses.

        :param emails: Email addresses.
        :param str stream_id: Message stream ID.
        :return: `EmailAddress`, `Status` (`Suppressed` or `Failed`) and `Message` per address.
        """
        return self._change(f"/message-streams/{stream_id}/suppressions", emails)

    def delete(self, emails: list[str], stream_id: str = DEFAULT_STREAM_ID) -> list[dict[str, Any]]:
        """Reactivates up to 50 addresses. `SpamComplaint` suppressions can't be deleted.

        :param emails: Email addresses.
        :param str stream_id: Message stream ID.
        :return: `EmailAddress`, `Status` (`Deleted` or `Failed`) and `Message` per address.
        """
        return self._change(f"/message-streams/{stream_id}/suppressions/delete", emails)

    def SubscriptionChange(self, json: str | bytes) -> SubscriptionChange:
        """Constructs a :py:class:`SubscriptionChange` from the subscription change webhook payload.

        :param json: `str`
        :rtype: :py:class:`SubscriptionChange`
        """
        return SubscriptionChange.from_json(json, manager=self)

    def _change(self, endpoint: str, emails: list[str]) -> list[dict[str, Any]]:
        data = {"Suppressions": [{"EmailAddress": email} for email in emails]}
        statuses: list[dict[str, Any]] = self.call("POST", endpoint, data=data)["Suppressions"]
        return statuses
