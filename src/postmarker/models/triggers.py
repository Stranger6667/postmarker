from __future__ import annotations

from typing import Any

from .base import Model, ModelManager, SubModelManager


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


class Tag(Model):
    def __str__(self) -> str:
        return str(self.MatchName)

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
