from __future__ import annotations

from typing import Any

from .base import AsyncModelManager, Model, ModelManager


class BaseAccountServer(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self._data.get("Name"),
            self._data.get("ID"),
        )


class AccountServer(BaseAccountServer):
    """A server of the account, managed with the account token."""

    def get(self) -> AccountServer:
        self._update(self._manager.get(self.ID).as_dict())
        return self

    def edit(self, **kwargs: Any) -> None:
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self) -> Any:
        return self._manager.delete(self.ID)


class ServersManager(ModelManager[AccountServer]):
    """Lets you list, get, create, edit or delete servers of the account."""

    name = "servers"
    model = AccountServer
    token_type = "account"

    def all(self, count: int | None = 500, offset: int = 0, name: str | None = None) -> list[AccountServer]:
        """Returns servers, filtered by a substring of their name if `name` is given."""
        responses = self.call_many("GET", "/servers", count=count, offset=offset, name=name)
        return self.expand_responses(responses, "Servers")

    def get(self, id: int) -> AccountServer:
        response = self.call("GET", f"/servers/{id}")
        return self._init_instance(response)

    def create(self, Name: str, **kwargs: Any) -> AccountServer:
        """Creates a server; other fields from Postmark's Servers API go as keyword arguments."""
        data = {"Name": Name, **kwargs}
        return self._init_instance(self.call("POST", "/servers", data=data))

    def edit(self, id: int, **kwargs: Any) -> Any:
        return self.call("PUT", f"/servers/{id}", data=kwargs)

    def delete(self, id: int) -> Any:
        return self.call("DELETE", f"/servers/{id}")["Message"]


class AsyncAccountServer(BaseAccountServer):
    """Async twin of :py:class:`AccountServer`."""

    async def get(self) -> AsyncAccountServer:
        self._update((await self._manager.get(self.ID)).as_dict())
        return self

    async def edit(self, **kwargs: Any) -> None:
        response = await self._manager.edit(self.ID, **kwargs)
        self._update(response)

    async def delete(self) -> Any:
        return await self._manager.delete(self.ID)


class AsyncServersManager(AsyncModelManager[AsyncAccountServer]):
    """Async twin of :py:class:`ServersManager`."""

    name = "servers"
    model = AsyncAccountServer
    token_type = "account"

    async def all(self, count: int | None = 500, offset: int = 0, name: str | None = None) -> list[AsyncAccountServer]:
        responses = await self.call_many("GET", "/servers", count=count, offset=offset, name=name)
        return self.expand_responses(responses, "Servers")

    async def get(self, id: int) -> AsyncAccountServer:
        response = await self.call("GET", f"/servers/{id}")
        return self._init_instance(response)

    async def create(self, Name: str, **kwargs: Any) -> AsyncAccountServer:
        data = {"Name": Name, **kwargs}
        return self._init_instance(await self.call("POST", "/servers", data=data))

    async def edit(self, id: int, **kwargs: Any) -> Any:
        return await self.call("PUT", f"/servers/{id}", data=kwargs)

    async def delete(self, id: int) -> Any:
        return (await self.call("DELETE", f"/servers/{id}"))["Message"]
