from unittest.mock import patch

import pytest

from postmarker.models.bounces import Bounce
from postmarker.models.messages import OutboundMessage

from ..conftest import BOUNCE_WEBHOOK

pytestmark = pytest.mark.vcr


def test_model_get(bounce):
    assert isinstance(bounce, Bounce)
    assert bounce.Inactive


def test_model_str(bounce):
    assert str(bounce) == "Bounce: 723626745"


def test_model_repr(bounce):
    assert repr(bounce) == "<Bounce: 723626745>"


def test_model_dump(bounce):
    assert bounce.dump is None


def test_model_activate(bounce):
    assert bounce.activate() == "OK"
    assert not bounce.Inactive


def test_manager_tags(postmark):
    assert postmark.bounces.tags == []


def test_manager_deliverystats(postmark):
    assert postmark.bounces.deliverystats == {
        "Bounces": [
            {"Count": 141, "Name": "All"},
            {"Count": 136, "Name": "Hard bounce", "Type": "HardBounce"},
            {"Count": 4, "Name": "Soft bounce", "Type": "SoftBounce"},
            {"Count": 1, "Name": "Spam complaint", "Type": "SpamComplaint"},
        ],
        "InactiveMails": 136,
    }


def test_manager_all(postmark):
    bounces = postmark.bounces.all(count=2)
    assert len(bounces) == 2
    assert all(isinstance(bounce, Bounce) for bounce in bounces)


def test_manager_init_bounce(postmark):
    bounce = postmark.bounces.Bounce(BOUNCE_WEBHOOK)
    assert bounce._manager is postmark.bounces


@pytest.mark.parametrize(
    "count, chunk_size, call_count",
    ((2, 50, 1), (2, 1, 2), (4, 1, 2), (None, 1, 2)),
)
def test_load_all_bounces_multiple_calls(postmark, count, chunk_size, call_count):
    with (
        patch.object(postmark.bounces, "max_chunk_size", chunk_size),
        patch.object(postmark.bounces, "call", wraps=postmark.bounces.call) as call,
    ):
        bounces = postmark.bounces.all(count=count)
        assert call.call_count == call_count
        assert len(bounces) == 2
        assert all(isinstance(bounce, Bounce) for bounce in bounces)


def test_message(bounce):
    message = bounce.message
    assert isinstance(message, OutboundMessage)
    assert str(message) == "Sent message to test@example.com"
