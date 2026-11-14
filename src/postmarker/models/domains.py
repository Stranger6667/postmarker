from __future__ import annotations

from typing import Any

from .base import AsyncModelManager, Model, ModelManager


class BaseDomain(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self._data.get("Name"),
            self._data.get("ID"),
        )


class Domain(BaseDomain):
    def get(self) -> Domain:
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs: Any) -> None:
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self) -> Any:
        return self._manager.delete(self.ID)

    def verifyspf(self) -> Any:
        return self._manager.verifyspf(self.ID)

    def verifydkim(self) -> Any:
        return self._manager.verifydkim(self.ID)

    def verifyreturnpath(self) -> Any:
        return self._manager.verifyreturnpath(self.ID)

    def rotatedkim(self) -> Any:
        return self._manager.rotatedkim(self.ID)


class DomainsManager(ModelManager[Domain]):
    name = "domains"
    model = Domain
    token_type = "account"

    def get(self, id: int) -> Domain:
        response = self.call("GET", f"/domains/{id}")
        return self._init_instance(response)

    def create(self, Name: str, ReturnPathDomain: str | None = None) -> Domain:
        data = {"Name": Name, "ReturnPathDomain": ReturnPathDomain}
        return self._init_instance(self.call("POST", "/domains", data=data))

    def edit(self, id: int, ReturnPathDomain: str) -> Any:
        data = {"ReturnPathDomain": ReturnPathDomain}
        return self.call("PUT", f"/domains/{id}", data=data)

    def all(self, count: int | None = 500, offset: int = 0) -> list[Domain]:
        responses = self.call_many("GET", "/domains", count=count, offset=offset)
        return self.expand_responses(responses, "Domains")

    def delete(self, id: int) -> Any:
        return self.call("DELETE", f"/domains/{id}")["Message"]

    def verifyspf(self, id: int) -> Any:
        return self.call("POST", f"/domains/{id}/verifyspf")

    def verifydkim(self, id: int) -> Any:
        return self.call("PUT", f"/domains/{id}/verifyDkim")

    def verifyreturnpath(self, id: int) -> Any:
        return self.call("PUT", f"/domains/{id}/verifyReturnPath")

    def rotatedkim(self, id: int) -> Any:
        return self.call("POST", f"/domains/{id}/rotatedkim")


class AsyncDomain(BaseDomain):
    """Async twin of :py:class:`Domain`."""

    async def get(self) -> AsyncDomain:
        new_instance = await self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    async def edit(self, **kwargs: Any) -> None:
        response = await self._manager.edit(self.ID, **kwargs)
        self._update(response)

    async def delete(self) -> Any:
        return await self._manager.delete(self.ID)

    async def verifyspf(self) -> Any:
        return await self._manager.verifyspf(self.ID)

    async def verifydkim(self) -> Any:
        return await self._manager.verifydkim(self.ID)

    async def verifyreturnpath(self) -> Any:
        return await self._manager.verifyreturnpath(self.ID)

    async def rotatedkim(self) -> Any:
        return await self._manager.rotatedkim(self.ID)


class AsyncDomainsManager(AsyncModelManager[AsyncDomain]):
    """Async twin of :py:class:`DomainsManager`."""

    name = "domains"
    model = AsyncDomain
    token_type = "account"

    async def get(self, id: int) -> AsyncDomain:
        response = await self.call("GET", f"/domains/{id}")
        return self._init_instance(response)

    async def create(self, Name: str, ReturnPathDomain: str | None = None) -> AsyncDomain:
        data = {"Name": Name, "ReturnPathDomain": ReturnPathDomain}
        return self._init_instance(await self.call("POST", "/domains", data=data))

    async def edit(self, id: int, ReturnPathDomain: str) -> Any:
        data = {"ReturnPathDomain": ReturnPathDomain}
        return await self.call("PUT", f"/domains/{id}", data=data)

    async def all(self, count: int | None = 500, offset: int = 0) -> list[AsyncDomain]:
        responses = await self.call_many("GET", "/domains", count=count, offset=offset)
        return self.expand_responses(responses, "Domains")

    async def delete(self, id: int) -> Any:
        return (await self.call("DELETE", f"/domains/{id}"))["Message"]

    async def verifyspf(self, id: int) -> Any:
        return await self.call("POST", f"/domains/{id}/verifyspf")

    async def verifydkim(self, id: int) -> Any:
        return await self.call("PUT", f"/domains/{id}/verifyDkim")

    async def verifyreturnpath(self, id: int) -> Any:
        return await self.call("PUT", f"/domains/{id}/verifyReturnPath")

    async def rotatedkim(self, id: int) -> Any:
        return await self.call("POST", f"/domains/{id}/rotatedkim")
