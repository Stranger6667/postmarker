# coding: utf-8
import json

import pytest

from .conftest import BOUNCE_WEBHOOK, DELIVERY_WEBHOOK, OPEN_WEBHOOK
from .helpers import recursive_gettatr


DECODED_DELIVERY_HOOK = json.loads(DELIVERY_WEBHOOK)


@pytest.mark.parametrize('attribute', DECODED_DELIVERY_HOOK.keys())
def test_delivery_webhook(delivery_webhook, attribute):
    assert getattr(delivery_webhook, attribute) == delivery_webhook._data[attribute]


@pytest.mark.parametrize('constructor, data', (
    ('bounces.Bounce', BOUNCE_WEBHOOK),
    ('messages.outbound.Open', OPEN_WEBHOOK),
))
def test_attributes(postmark, constructor, data):
    instance = recursive_gettatr(postmark, constructor)(data)
    for attribute in json.loads(data):
        assert getattr(instance, attribute) == instance._data[attribute]
