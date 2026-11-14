from functools import reduce
from unittest.mock import patch

import pytest

from postmarker.core import USER_AGENT
from postmarker.models.base import Model, ModelManager, SubModelManager
from postmarker.models.bounces import BounceManager

from ..conftest import aw, twin

pytestmark = pytest.mark.anyio


def test_model_as_dict():
    instance = Model(value=1)
    assert instance.as_dict() == {"value": 1}


def test_model_str():
    instance = Model(ID=1)
    assert str(instance) == "Model: 1"


def test_model_manager_str():
    assert str(ModelManager(None)) == "ModelManager"


def test_model_manager_repr():
    assert repr(ModelManager(None)) == "<ModelManager>"


async def requested_pages(client, path, total, **kwargs):
    manager = reduce(getattr, path.split("."), client)
    response = {"TotalCount": total, "Bounces": [], "Messages": [], "InboundMessages": [], "Opens": [], "Domains": []}
    with patch.object(manager, "call", return_value=response) as call:
        await aw(manager.all(**kwargs))
    return [(c.kwargs["count"], c.kwargs["offset"]) for c in call.call_args_list]


UP_TO_LIMIT = [(500, offset) for offset in range(0, 10000, 500)]


LIMITED = (
    ({"count": None}, UP_TO_LIMIT),
    ({"count": 20000}, UP_TO_LIMIT),
    ({"count": None, "offset": 9800}, [(200, 9800)]),
    ({"count": 500, "offset": 9800}, [(200, 9800)]),
    ({"count": None, "offset": 10000}, []),
)


@pytest.mark.parametrize("path", ("bounces", "messages.outbound", "messages.inbound", "messages.outbound.opens"))
@pytest.mark.parametrize("kwargs, expected", LIMITED)
async def test_pagination_limit(client, path, kwargs, expected):
    # Postmark rejects search requests where count + offset exceeds 10,000
    assert await requested_pages(client, path, 25000, **kwargs) == expected


async def test_no_pagination_limit(client):
    pages = await requested_pages(client, "domains", 25000, count=None)
    assert pages == [(500, offset) for offset in range(0, 25000, 500)]


@pytest.mark.parametrize(
    ("kwargs", "header"),
    (
        ({}, {"X-Postmark-Server-Token": "SERVER_TOKEN"}),
        ({"token_type": "account"}, {"X-Postmark-Account-Token": "ACCOUNT_TOKEN"}),
    ),
)
async def test_manager_call_token_type(client, api_request, kwargs, header):
    await aw(client.bounces.call("GET", "/bounces", **kwargs))
    assert api_request.call_args[1]["headers"] == {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        **header,
    }


def test_sub_model_manager_attaches_managers(flavor):
    class Holder(twin(SubModelManager, flavor)):
        _managers = (twin(BounceManager, flavor),)

    holder = Holder("client")
    assert isinstance(holder.bounces, twin(BounceManager, flavor))
    assert holder.bounces.client == "client"
