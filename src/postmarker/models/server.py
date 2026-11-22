from __future__ import annotations

from typing import Any, Unpack

from .base import AsyncModelManager, Model, ModelManager
from .servers import ServerSettings


class BaseServer(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self.Name,
            self._data.get("ID"),
        )


class Server(BaseServer):
    def edit(self, **kwargs: Unpack[ServerSettings]) -> None:
        response = self._manager.edit(**kwargs)
        self._update(response)


class ServerManager(ModelManager[Server]):
    """Lets you get or edit details of the specific server."""

    name = "server"
    model = Server

    def get(self) -> Server:
        response = self.call("GET", "/server")
        return self._init_instance(response)

    def edit(self, **kwargs: Unpack[ServerSettings]) -> Any:
        return self.call("PUT", "/server", data=kwargs)


class AsyncServer(BaseServer):
    """Async twin of :py:class:`Server`."""

    async def edit(self, **kwargs: Unpack[ServerSettings]) -> None:
        response = await self._manager.edit(**kwargs)
        self._update(response)


class AsyncServerManager(AsyncModelManager[AsyncServer]):
    """Async twin of :py:class:`ServerManager`."""

    name = "server"
    model = AsyncServer

    async def get(self) -> AsyncServer:
        response = await self.call("GET", "/server")
        return self._init_instance(response)

    async def edit(self, **kwargs: Unpack[ServerSettings]) -> Any:
        return await self.call("PUT", "/server", data=kwargs)
