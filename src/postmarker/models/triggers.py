from __future__ import annotations

from typing import Any

from .base import AsyncModelManager, AsyncSubModelManager, Model, ModelManager, SubModelManager


class InboundRule(Model):
    def delete(self) -> Any:
        return self._manager.delete(self.ID)


class InboundRulesManager(ModelManager[InboundRule]):
    name = "inboundrules"
    model = InboundRule

    def all(self, count: int | None = 500, offset: int = 0) -> list[InboundRule]:
        responses = self.call_many("GET", "/triggers/inboundrules", count=count, offset=offset)
        return self.expand_responses(responses, "InboundRules")

    def create(self, Rule: str) -> InboundRule:
        return self._init_instance(self.call("POST", "/triggers/inboundrules", data={"Rule": Rule}))

    def delete(self, id: int) -> Any:
        return self.call("DELETE", f"/triggers/inboundrules/{id}")["Message"]


class BaseTag(Model):
    def __str__(self) -> str:
        return str(self.MatchName)


class Tag(BaseTag):
    def get(self) -> Tag:
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs: Any) -> None:
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self) -> Any:
        return self._manager.delete(self.ID)


class TagsTriggersManager(ModelManager[Tag]):
    name = "tags"
    model = Tag

    def all(self, count: int | None = 500, offset: int = 0, match_name: str | None = None) -> list[Tag]:
        responses = self.call_many("GET", "/triggers/tags", count=count, offset=offset, match_name=match_name)
        return self.expand_responses(responses, "Tags")

    def create(self, MatchName: str, TrackOpens: bool | None = None) -> Tag:
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return self._init_instance(self.call("POST", "/triggers/tags", data=data))

    def get(self, id: int) -> Tag:
        response = self.call("GET", f"/triggers/tags/{id}")
        return self._init_instance(response)

    def edit(self, id: int, MatchName: str, TrackOpens: bool | None = None) -> Any:
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return self.call("PUT", f"/triggers/tags/{id}", data=data)

    def delete(self, id: int) -> Any:
        return self.call("DELETE", f"/triggers/tags/{id}")["Message"]


class TriggersManager(SubModelManager[Model]):
    name = "triggers"
    inboundrules: InboundRulesManager
    tags: TagsTriggersManager
    _managers = (InboundRulesManager, TagsTriggersManager)


class AsyncInboundRule(Model):
    """Async twin of :py:class:`InboundRule`."""

    async def delete(self) -> Any:
        return await self._manager.delete(self.ID)


class AsyncInboundRulesManager(AsyncModelManager[AsyncInboundRule]):
    """Async twin of :py:class:`InboundRulesManager`."""

    name = "inboundrules"
    model = AsyncInboundRule

    async def all(self, count: int | None = 500, offset: int = 0) -> list[AsyncInboundRule]:
        responses = await self.call_many("GET", "/triggers/inboundrules", count=count, offset=offset)
        return self.expand_responses(responses, "InboundRules")

    async def create(self, Rule: str) -> AsyncInboundRule:
        return self._init_instance(await self.call("POST", "/triggers/inboundrules", data={"Rule": Rule}))

    async def delete(self, id: int) -> Any:
        return (await self.call("DELETE", f"/triggers/inboundrules/{id}"))["Message"]


class AsyncTag(BaseTag):
    """Async twin of :py:class:`Tag`."""

    async def get(self) -> AsyncTag:
        new_instance = await self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    async def edit(self, **kwargs: Any) -> None:
        response = await self._manager.edit(self.ID, **kwargs)
        self._update(response)

    async def delete(self) -> Any:
        return await self._manager.delete(self.ID)


class AsyncTagsTriggersManager(AsyncModelManager[AsyncTag]):
    """Async twin of :py:class:`TagsTriggersManager`."""

    name = "tags"
    model = AsyncTag

    async def all(self, count: int | None = 500, offset: int = 0, match_name: str | None = None) -> list[AsyncTag]:
        responses = await self.call_many("GET", "/triggers/tags", count=count, offset=offset, match_name=match_name)
        return self.expand_responses(responses, "Tags")

    async def create(self, MatchName: str, TrackOpens: bool | None = None) -> AsyncTag:
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return self._init_instance(await self.call("POST", "/triggers/tags", data=data))

    async def get(self, id: int) -> AsyncTag:
        response = await self.call("GET", f"/triggers/tags/{id}")
        return self._init_instance(response)

    async def edit(self, id: int, MatchName: str, TrackOpens: bool | None = None) -> Any:
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return await self.call("PUT", f"/triggers/tags/{id}", data=data)

    async def delete(self, id: int) -> Any:
        return (await self.call("DELETE", f"/triggers/tags/{id}"))["Message"]


class AsyncTriggersManager(AsyncSubModelManager[Model]):
    """Async twin of :py:class:`TriggersManager`."""

    name = "triggers"
    inboundrules: AsyncInboundRulesManager
    tags: AsyncTagsTriggersManager
    _managers = (AsyncInboundRulesManager, AsyncTagsTriggersManager)
