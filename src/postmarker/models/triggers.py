# pylint: disable=redefined-builtin
from .base import Model, ModelManager, SubModelManager


class InboundRule(Model):
    def delete(self):
        return self._manager.delete(self.ID)


class InboundRulesManager(ModelManager):
    name = "inboundrules"
    model = InboundRule

    def all(self, count=500, offset=0):
        responses = self.call_many("GET", "/triggers/inboundrules", count=count, offset=offset)
        return self.expand_responses(responses, "InboundRules")

    def create(self, Rule):
        return self._init_instance(self.call("POST", "/triggers/inboundrules", data={"Rule": Rule}))

    def delete(self, id):
        return self.call("DELETE", "/triggers/inboundrules/%s" % id)["Message"]


class Tag(Model):
    def __str__(self):
        return self.MatchName

    def get(self):
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs):
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self):
        return self._manager.delete(self.ID)


class TagsTriggersManager(ModelManager):
    name = "tags"
    model = Tag

    def all(self, count=500, offset=0, match_name=None):
        responses = self.call_many("GET", "/triggers/tags", count=count, offset=offset, match_name=match_name)
        return self.expand_responses(responses, "Tags")

    def create(self, MatchName, TrackOpens=None):
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return self._init_instance(self.call("POST", "/triggers/tags", data=data))

    def get(self, id):
        response = self.call("GET", "/triggers/tags/%s" % id)
        return self._init_instance(response)

    def edit(self, id, MatchName, TrackOpens=None):
        data = {"MatchName": MatchName, "TrackOpens": TrackOpens}
        return self.call("PUT", "/triggers/tags/%s" % id, data=data)

    def delete(self, id):
        return self.call("DELETE", "/triggers/tags/%s" % id)["Message"]


class TriggersManager(SubModelManager):
    name = "triggers"
    _managers = (InboundRulesManager, TagsTriggersManager)
