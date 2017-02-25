# coding: utf-8
from postmarker.models.base import ModelManager


def test_sub_managers(postmark):
    outbound = postmark.messages.outbound
    assert isinstance(outbound, ModelManager)
    assert outbound.client is postmark

    inbound = postmark.messages.inbound
    assert isinstance(inbound, ModelManager)
    assert inbound.client is postmark

    opens = postmark.messages.outbound.opens
    assert isinstance(opens, ModelManager)
    assert opens.client is postmark
