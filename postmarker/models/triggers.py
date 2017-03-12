# coding: utf-8
from .base import Model, ModelManager, SubModelManager


class InboundRule(Model):

    def delete(self):
        return self._manager.delete(self.ID)


class InboundRulesManager(ModelManager):
    name = 'inboundrules'
    model = InboundRule

    def all(self, count=500, offset=0):
        responses = self.call_many('GET', '/triggers/inboundrules', count=count, offset=offset)
        return self.expand_responses(responses, 'InboundRules')

    def create(self, Rule):
        return self._init_instance(self.call('POST', '/triggers/inboundrules', data={'Rule': Rule}))

    def delete(self, id):
        return self.call('DELETE', '/triggers/inboundrules/%s' % id)['Message']


class TriggersManager(SubModelManager):
    name = 'triggers'
    _managers = (
        InboundRulesManager,
    )
