from unittest.mock import patch

import pytest

from postmarker.models.bounces import Bounce
from postmarker.models.messages import OutboundMessage

from ..conftest import BOUNCE_WEBHOOK, aw, twin

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


async def get_bounce(client):
    return await aw(client.bounces.get(723626745))


async def test_model_get(client, flavor):
    bounce = await get_bounce(client)
    assert isinstance(bounce, twin(Bounce, flavor))
    assert bounce.Inactive


async def test_model_str(client, flavor):
    assert str(await get_bounce(client)) == f"{twin(Bounce, flavor).__name__}: 723626745"


async def test_model_repr(client, flavor):
    assert repr(await get_bounce(client)) == f"<{twin(Bounce, flavor).__name__}: 723626745>"


async def test_model_dump(client):
    bounce = await get_bounce(client)
    assert await aw(bounce.dump) is None


async def test_model_activate(client, flavor):
    bounce = await get_bounce(client)
    assert isinstance(bounce, twin(Bounce, flavor))
    assert await aw(bounce.activate()) == "OK"
    assert not bounce.Inactive


async def test_manager_tags(client):
    assert await aw(client.bounces.tags) == []


async def test_manager_deliverystats(client):
    assert await aw(client.bounces.deliverystats) == {
        "Bounces": [
            {"Count": 141, "Name": "All"},
            {"Count": 136, "Name": "Hard bounce", "Type": "HardBounce"},
            {"Count": 4, "Name": "Soft bounce", "Type": "SoftBounce"},
            {"Count": 1, "Name": "Spam complaint", "Type": "SpamComplaint"},
        ],
        "InactiveMails": 136,
    }


async def test_manager_all(client, flavor):
    bounces = await aw(client.bounces.all(count=2))
    assert len(bounces) == 2
    assert all(isinstance(bounce, twin(Bounce, flavor)) for bounce in bounces)


async def test_manager_init_bounce(client, flavor):
    bounce = client.bounces.Bounce(BOUNCE_WEBHOOK)
    assert isinstance(bounce, twin(Bounce, flavor))
    assert bounce._manager is client.bounces


@pytest.mark.parametrize(
    "count, chunk_size, call_count",
    ((2, 50, 1), (2, 1, 2), (4, 1, 2), (None, 1, 2)),
)
async def test_load_all_bounces_multiple_calls(client, flavor, count, chunk_size, call_count):
    with (
        patch.object(client.bounces, "max_chunk_size", chunk_size),
        patch.object(client.bounces, "call", wraps=client.bounces.call) as call,
    ):
        bounces = await aw(client.bounces.all(count=count))
        assert call.call_count == call_count
        assert len(bounces) == 2
        assert all(isinstance(bounce, twin(Bounce, flavor)) for bounce in bounces)


async def test_message(client, flavor):
    message = await aw((await get_bounce(client)).message)
    assert isinstance(message, twin(OutboundMessage, flavor))
    assert str(message) == "Sent message to test@example.com"
