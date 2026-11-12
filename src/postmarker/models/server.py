from __future__ import annotations

from typing import Any

from .base import Model, ModelManager


class Server(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self.Name,
            self._data.get("ID"),
        )

    def edit(self, **kwargs: Any) -> None:
        response = self._manager.edit(**kwargs)
        self._update(response)


class ServerManager(ModelManager[Server]):
    """Lets you get or edit details of the specific server."""

    name = "server"
    model = Server

    def get(self) -> Server:
        response = self.call("GET", "/server")
        return self._init_instance(response)

    def edit(self, **kwargs: Any) -> Any:
        return self.call("PUT", "/server", data=kwargs)
