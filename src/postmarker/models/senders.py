from __future__ import annotations

import warnings
from typing import Any

from .base import AsyncModelManager, Model, ModelManager


def with_note(data: dict[str, Any], note: str | None) -> dict[str, Any]:
    # Sent only when given: Postmark doesn't document what `null` does
    if note is not None:
        data["ConfirmationPersonalNote"] = note
    return data


def warn_requestnewdkim() -> None:
    warnings.warn(
        "This method has been deprecated. "
        "Please use the new Domains API (http://developer.postmarkapp.com/developer-api-domains.html) "
        "for updated SPF methods.",
        DeprecationWarning,
        # The caller of `requestnewdkim`
        stacklevel=3,
    )


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
        return self._init_instance(self.call("POST", "/senders/", data=with_note(data, ConfirmationPersonalNote)))

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
        return self.call("PUT", f"/senders/{id}", data=with_note(data, ConfirmationPersonalNote))

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
        warn_requestnewdkim()
        return self.call("POST", f"/senders/{id}/requestnewdkim")


class AsyncSenderSignature(Model):
    """Async twin of :py:class:`SenderSignature`."""

    async def get(self) -> AsyncSenderSignature:
        new_instance = await self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    async def edit(self, **kwargs: Any) -> None:
        response = await self._manager.edit(self.ID, **kwargs)
        self._update(response)

    async def delete(self) -> Any:
        return await self._manager.delete(self.ID)

    async def resend(self) -> Any:
        return await self._manager.resend(self.ID)

    async def verifyspf(self) -> Any:
        return await self._manager.verifyspf(self.ID)

    async def requestnewdkim(self) -> Any:
        return await self._manager.requestnewdkim(self.ID)


class AsyncSenderSignaturesManager(AsyncModelManager[AsyncSenderSignature]):
    """Async twin of :py:class:`SenderSignaturesManager`."""

    name = "senders"
    model = AsyncSenderSignature
    token_type = "account"

    async def all(self, count: int | None = 500, offset: int = 0) -> list[AsyncSenderSignature]:
        responses = await self.call_many("GET", "/senders/", count=count, offset=offset)
        return self.expand_responses(responses, "SenderSignatures")

    async def get(self, id: int) -> AsyncSenderSignature:
        response = await self.call("GET", f"/senders/{id}")
        return self._init_instance(response)

    async def create(
        self,
        FromEmail: str,
        Name: str,
        ReplyToEmail: str | None = None,
        ReturnPathDomain: str | None = None,
        ConfirmationPersonalNote: str | None = None,
    ) -> AsyncSenderSignature:
        data = {
            "FromEmail": FromEmail,
            "Name": Name,
            "ReplyToEmail": ReplyToEmail,
            "ReturnPathDomain": ReturnPathDomain,
        }
        return self._init_instance(await self.call("POST", "/senders/", data=with_note(data, ConfirmationPersonalNote)))

    async def edit(
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
        return await self.call("PUT", f"/senders/{id}", data=with_note(data, ConfirmationPersonalNote))

    async def delete(self, id: int) -> Any:
        return (await self.call("DELETE", f"/senders/{id}"))["Message"]

    async def resend(self, id: int) -> Any:
        return (await self.call("POST", f"/senders/{id}/resend"))["Message"]

    async def verifyspf(self, id: int) -> Any:
        return await self.call("POST", f"/senders/{id}/verifyspf")

    async def requestnewdkim(self, id: int) -> Any:
        warn_requestnewdkim()
        return await self.call("POST", f"/senders/{id}/requestnewdkim")
