import pytest
from requests import Request

from postmarker.core import USER_AGENT
from postmarker.models.suppressions import Suppression, SuppressionsManager

from ..conftest import aw, twin

pytestmark = pytest.mark.anyio

# Response shapes from https://postmarkapp.com/developer/api/suppressions-api
DUMP = {
    "Suppressions": [
        {
            "EmailAddress": "address@wildbit.com",
            "SuppressionReason": "ManualSuppression",
            "Origin": "Recipient",
            "CreatedAt": "2019-12-17T08:58:33-05:00",
        },
        {
            "EmailAddress": "bounce.address@wildbit.com",
            "SuppressionReason": "HardBounce",
            "Origin": "Recipient",
            "CreatedAt": "2019-12-17T08:58:33-05:00",
        },
    ]
}
CREATED = {
    "Suppressions": [
        {"EmailAddress": "good.address@wildbit.com", "Status": "Suppressed", "Message": None},
        {
            "EmailAddress": "invalid-email-address",
            "Status": "Failed",
            "Message": "An invalid email address was provided.",
        },
    ]
}
DELETED = {
    "Suppressions": [
        {"EmailAddress": "good.address@wildbit.com", "Status": "Deleted", "Message": None},
        {
            "EmailAddress": "spammy.address@wildbit.com",
            "Status": "Failed",
            "Message": "You do not have the required authority to change this suppression.",
        },
    ]
}
HEADERS = {
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
    "X-Postmark-Server-Token": "SERVER_TOKEN",
}
NO_FILTERS = {
    "SuppressionReason": None,
    "Origin": None,
    "fromdate": None,
    "todate": None,
    "EmailAddress": None,
}


async def test_manager(client, flavor):
    assert repr(client.suppressions) == f"<{twin(SuppressionsManager, flavor).__name__}>"


async def test_all(client, api_request):
    api_request.return_value.json.return_value = DUMP

    suppressions = await aw(client.suppressions.all())

    api_request.assert_called_once_with(
        "GET",
        "https://api.postmarkapp.com/message-streams/outbound/suppressions/dump",
        json=None,
        params=NO_FILTERS,
        headers=HEADERS,
        timeout=30,
    )
    assert all(isinstance(suppression, Suppression) for suppression in suppressions)
    assert [suppression.as_dict() for suppression in suppressions] == DUMP["Suppressions"]
    assert repr(suppressions[1]) == "<Suppression: bounce.address@wildbit.com>"
    assert suppressions[1].SuppressionReason == "HardBounce"


async def test_all_filters(client, api_request):
    api_request.return_value.json.return_value = {"Suppressions": DUMP["Suppressions"][1:]}

    suppressions = await aw(
        client.suppressions.all(
            "broadcast",
            SuppressionReason="HardBounce",
            Origin="Recipient",
            fromdate="2019-12-01",
            todate="2019-12-31",
            EmailAddress="bounce.address@wildbit.com",
        )
    )

    method, url = api_request.call_args[0]
    assert method == "GET"
    assert url == "https://api.postmarkapp.com/message-streams/broadcast/suppressions/dump"
    params = api_request.call_args[1]["params"]
    assert params == {
        "SuppressionReason": "HardBounce",
        "Origin": "Recipient",
        "fromdate": "2019-12-01",
        "todate": "2019-12-31",
        "EmailAddress": "bounce.address@wildbit.com",
    }
    # Each filter is its own query parameter, not one parameter named `params`
    assert Request(method, url, params=params).prepare().url == (
        "https://api.postmarkapp.com/message-streams/broadcast/suppressions/dump"
        "?SuppressionReason=HardBounce&Origin=Recipient&fromdate=2019-12-01&todate=2019-12-31"
        "&EmailAddress=bounce.address%40wildbit.com"
    )
    assert [suppression.as_dict() for suppression in suppressions] == DUMP["Suppressions"][1:]


@pytest.mark.parametrize(
    "kwargs, stream_id",
    (
        ({}, "outbound"),
        ({"stream_id": "broadcast"}, "broadcast"),
    ),
)
async def test_create(client, api_request, kwargs, stream_id):
    api_request.return_value.json.return_value = CREATED

    statuses = await aw(client.suppressions.create(["good.address@wildbit.com", "invalid-email-address"], **kwargs))

    api_request.assert_called_once_with(
        "POST",
        f"https://api.postmarkapp.com/message-streams/{stream_id}/suppressions",
        json={
            "Suppressions": [
                {"EmailAddress": "good.address@wildbit.com"},
                {"EmailAddress": "invalid-email-address"},
            ]
        },
        params={},
        headers=HEADERS,
        timeout=30,
    )
    assert statuses == [
        {"EmailAddress": "good.address@wildbit.com", "Status": "Suppressed", "Message": None},
        {
            "EmailAddress": "invalid-email-address",
            "Status": "Failed",
            "Message": "An invalid email address was provided.",
        },
    ]


@pytest.mark.parametrize(
    "kwargs, stream_id",
    (
        ({}, "outbound"),
        ({"stream_id": "broadcast"}, "broadcast"),
    ),
)
async def test_delete(client, api_request, kwargs, stream_id):
    api_request.return_value.json.return_value = DELETED

    statuses = await aw(
        client.suppressions.delete(["good.address@wildbit.com", "spammy.address@wildbit.com"], **kwargs)
    )

    api_request.assert_called_once_with(
        "POST",
        f"https://api.postmarkapp.com/message-streams/{stream_id}/suppressions/delete",
        json={
            "Suppressions": [
                {"EmailAddress": "good.address@wildbit.com"},
                {"EmailAddress": "spammy.address@wildbit.com"},
            ]
        },
        params={},
        headers=HEADERS,
        timeout=30,
    )
    assert statuses == [
        {"EmailAddress": "good.address@wildbit.com", "Status": "Deleted", "Message": None},
        {
            "EmailAddress": "spammy.address@wildbit.com",
            "Status": "Failed",
            "Message": "You do not have the required authority to change this suppression.",
        },
    ]
