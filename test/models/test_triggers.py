import pytest

from postmarker.models.base import ModelManager
from postmarker.models.triggers import InboundRule, Tag

from ..conftest import aw, twin

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


@pytest.mark.parametrize("name", ("inboundrules", "tags"))
async def test_triggers_manager(client, flavor, name):
    manager = getattr(client.triggers, name)
    assert isinstance(manager, twin(ModelManager, flavor))
    assert manager.client is client


async def test_inbound_rules_create(client, flavor):
    rule = await aw(client.triggers.inboundrules.create("someone@example.com"))
    assert isinstance(rule, twin(InboundRule, flavor))
    assert str(rule) == f"{twin(InboundRule, flavor).__name__}: 962286"


async def test_inbound_rules_all(client, flavor):
    rules = await aw(client.triggers.inboundrules.all())
    assert len(rules) == 1
    assert isinstance(rules[0], twin(InboundRule, flavor))


async def test_inbound_rules_delete(client):
    rule = (await aw(client.triggers.inboundrules.all()))[0]
    assert await aw(rule.delete()) == "Rule someone@example.com removed."


async def test_tags_create(client, flavor):
    tag = await aw(client.triggers.tags.create("welcome"))
    assert isinstance(tag, twin(Tag, flavor))
    assert str(tag) == "welcome"


async def test_tags_all(client, flavor):
    tags = await aw(client.triggers.tags.all())
    assert len(tags) == 1
    assert isinstance(tags[0], twin(Tag, flavor))


async def test_tags_get(client, flavor):
    tag = (await aw(client.triggers.tags.all()))[0]
    assert isinstance(await aw(tag.get()), twin(Tag, flavor))


async def test_tags_edit(client):
    tag = await aw(client.triggers.tags.create("welcome2"))
    await aw(tag.edit(MatchName="blabla"))
    assert tag.MatchName == "blabla"


async def test_tags_delete(client):
    tag = (await aw(client.triggers.tags.all()))[0]
    assert await aw(tag.delete()) == "Tag 1616731 removed."
