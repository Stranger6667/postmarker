from __future__ import annotations

from typing import Any

from .base import AsyncModelManager, Model, ModelManager


class BaseServer(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self.Name,
            self._data.get("ID"),
        )


class Server(BaseServer):
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


class AsyncServer(BaseServer):
    """Async twin of :py:class:`Server`."""

    async def edit(self, **kwargs: Any) -> None:
        response = await self._manager.edit(**kwargs)
        self._update(response)


class AsyncServerManager(AsyncModelManager[AsyncServer]):
    """Async twin of :py:class:`ServerManager`."""

    name = "server"
    model = AsyncServer

    async def get(self) -> AsyncServer:
        response = await self.call("GET", "/server")
        return self._init_instance(response)

    async def edit(self, **kwargs: Any) -> Any:
        return await self.call("PUT", "/server", data=kwargs)
