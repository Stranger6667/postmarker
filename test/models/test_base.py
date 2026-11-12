from functools import reduce
from unittest.mock import patch

import pytest

from postmarker.models.base import Model, ModelManager


class TestModel:
    def test_as_dict(self):
        instance = Model(value=1)
        assert instance.as_dict() == {"value": 1}

    def test_str(self):
        instance = Model(ID=1)
        assert str(instance) == "Model: 1"


class TestModelManager:
    def test_str(self):
        assert str(ModelManager(None)) == "ModelManager"

    def test_repr(self):
        assert repr(ModelManager(None)) == "<ModelManager>"


def requested_pages(postmark, path, total, **kwargs):
    manager = reduce(getattr, path.split("."), postmark)
    response = {"TotalCount": total, "Bounces": [], "Messages": [], "InboundMessages": [], "Opens": [], "Domains": []}
    with patch.object(manager, "call", return_value=response) as call:
        manager.all(**kwargs)
    return [(c.kwargs["count"], c.kwargs["offset"]) for c in call.call_args_list]


UP_TO_LIMIT = [(500, offset) for offset in range(0, 10000, 500)]


@pytest.mark.parametrize("path", ("bounces", "messages.outbound", "messages.inbound", "messages.outbound.opens"))
@pytest.mark.parametrize(
    "kwargs, expected",
    (
        ({"count": None}, UP_TO_LIMIT),
        ({"count": 20000}, UP_TO_LIMIT),
        ({"count": None, "offset": 9800}, [(200, 9800)]),
        ({"count": 500, "offset": 9800}, [(200, 9800)]),
        ({"count": None, "offset": 10000}, []),
    ),
)
def test_pagination_limit(postmark, path, kwargs, expected):
    # Postmark rejects search requests where count + offset exceeds 10,000
    assert requested_pages(postmark, path, 25000, **kwargs) == expected


def test_no_pagination_limit(postmark):
    assert requested_pages(postmark, "domains", 25000, count=None) == [(500, offset) for offset in range(0, 25000, 500)]
