from __future__ import annotations

import warnings
from typing import Any

from .base import Model, ModelManager


class SenderSignature(Model):
    def get(self) -> SenderSignature:
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs: Any) -> None:
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self) -> Any:
        return self._manager.delete(self.ID)

    def resend(self) -> Any:
        return self._manager.resend(self.ID)

    def verifyspf(self) -> Any:
        return self._manager.verifyspf(self.ID)

    def requestnewdkim(self) -> Any:
        return self._manager.requestnewdkim(self.ID)


class SenderSignaturesManager(ModelManager[SenderSignature]):
    name = "senders"
    model = SenderSignature
    token_type = "account"

    def all(self, count: int | None = 500, offset: int = 0) -> list[SenderSignature]:
        """Gets a list of sender signatures containing brief details associated with your account."""
        responses = self.call_many("GET", "/senders/", count=count, offset=offset)
        return self.expand_responses(responses, "SenderSignatures")

    def get(self, id: int) -> SenderSignature:
        """Gets all the details for a specific sender signature."""
        response = self.call("GET", f"/senders/{id}")
        return self._init_instance(response)

    def create(
        self,
        FromEmail: str,
        Name: str,
        ReplyToEmail: str | None = None,
        ReturnPathDomain: str | None = None,
        ConfirmationPersonalNote: str | None = None,
    ) -> SenderSignature:
        """Creates a sender signature; `ConfirmationPersonalNote` goes to the confirmation email (max 400 chars)."""
        data = {
            "FromEmail": FromEmail,
            "Name": Name,
            "ReplyToEmail": ReplyToEmail,
            "ReturnPathDomain": ReturnPathDomain,
        }
        # Sent only when given: Postmark doesn't document what `null` does
        if ConfirmationPersonalNote is not None:
            data["ConfirmationPersonalNote"] = ConfirmationPersonalNote
        return self._init_instance(self.call("POST", "/senders/", data=data))

    def edit(
        self,
        id: int,
        Name: str,
        ReplyToEmail: str | None = None,
        ReturnPathDomain: str | None = None,
        ConfirmationPersonalNote: str | None = None,
    ) -> Any:
        data = {
            "Name": Name,
            "ReplyToEmail": ReplyToEmail,
            "ReturnPathDomain": ReturnPathDomain,
        }
        if ConfirmationPersonalNote is not None:
            data["ConfirmationPersonalNote"] = ConfirmationPersonalNote
        return self.call("PUT", f"/senders/{id}", data=data)

    def delete(self, id: int) -> Any:
        return self.call("DELETE", f"/senders/{id}")["Message"]

    def resend(self, id: int) -> Any:
        return self.call("POST", f"/senders/{id}/resend")["Message"]

    def verifyspf(self, id: int) -> Any:
        return self.call("POST", f"/senders/{id}/verifyspf")

    def requestnewdkim(self, id: int) -> Any:
        """Request new DKIM.

        Will query DNS for your domain and attempt to verify the SPF record contains the information for
        Postmark's servers.
        """
        warnings.warn(
            "This method has been deprecated. "
            "Please use the new Domains API (http://developer.postmarkapp.com/developer-api-domains.html) "
            "for updated SPF methods.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.call("POST", f"/senders/{id}/requestnewdkim")
