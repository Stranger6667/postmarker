import pytest

from postmarker.models.base import ModelManager
from postmarker.models.triggers import InboundRule, Tag

CASSETTE_NAME = "triggers"


@pytest.mark.parametrize("name", ("inboundrules", "tags"))
def test_triggers_manager(postmark, name):
    manager = getattr(postmark.triggers, name)
    assert isinstance(manager, ModelManager)
    assert manager.client is postmark


class TestInboundRulesTriggers:
    def test_create(self, postmark):
        rule = postmark.triggers.inboundrules.create("someone@example.com")
        assert isinstance(rule, InboundRule)
        assert str(rule) == "InboundRule: 962286"

    def test_all(self, postmark):
        rules = postmark.triggers.inboundrules.all()
        assert len(rules) == 1
        assert isinstance(rules[0], InboundRule)

    def test_delete(self, postmark):
        rule = postmark.triggers.inboundrules.all()[0]
        assert rule.delete() == "Rule someone@example.com removed."


class TestTagsTriggers:
    def test_create(self, postmark):
        tag = postmark.triggers.tags.create("welcome")
        assert isinstance(tag, Tag)
        assert str(tag) == "welcome"

    def test_all(self, postmark):
        tags = postmark.triggers.tags.all()
        assert len(tags) == 1
        assert isinstance(tags[0], Tag)

    def test_get(self, postmark):
        tag = postmark.triggers.tags.all()[0]
        assert isinstance(tag.get(), Tag)

    def test_edit(self, postmark):
        tag = postmark.triggers.tags.create("welcome2")
        tag.edit(MatchName="blabla")
        assert tag.MatchName == "blabla"

    def test_delete(self, postmark):
        tag = postmark.triggers.tags.all()[0]
        assert tag.delete() == "Tag 1616731 removed."
