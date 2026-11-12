from __future__ import annotations

from typing import Any

from .base import Model, ModelManager


class AccountServer(Model):
    """A server of the account, managed with the account token."""

    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self._data.get("Name"),
            self._data.get("ID"),
        )

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
