# coding: utf-8
from postmarker.models.base import ModelManager
from postmarker.models.triggers import InboundRule


CASSETTE_NAME = 'triggers'


def test_triggers_manager(postmark):
    inboundrules = postmark.triggers.inboundrules
    assert isinstance(inboundrules, ModelManager)
    assert inboundrules.client is postmark


class TestInboundRulesTriggers:

    def test_create(self, postmark):
        rule = postmark.triggers.inboundrules.create('someone@example.com')
        assert isinstance(rule, InboundRule)
        assert str(rule) == 'InboundRule: 962286'

    def test_all(self, postmark):
        rules = postmark.triggers.inboundrules.all()
        assert len(rules) == 1
        assert isinstance(rules[0], InboundRule)

    def test_delete(self, postmark):
        rule = postmark.triggers.inboundrules.all()[0]
        assert rule.delete() == 'Rule someone@example.com removed.'
