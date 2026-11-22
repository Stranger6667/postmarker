import pytest

from postmarker.core import USER_AGENT
from postmarker.models.message_streams import MessageStream, MessageStreamsManager

from ..conftest import aw, twin

pytestmark = pytest.mark.anyio

# Shaped like the response examples at https://postmarkapp.com/developer/api/message-streams-api
BROADCASTS = {
    "ID": "broadcasts",
    "ServerID": 123456,
    "Name": "Broadcast Stream",
    "Description": "This is my stream to send broadcast messages",
    "MessageStreamType": "Broadcasts",
    "CreatedAt": "2020-07-01T00:00:00-04:00",
    "UpdatedAt": "2020-07-01T00:00:00-04:00",
    "ArchivedAt": None,
    "ExpectedPurgeDate": None,
    "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "Postmark"},
}
LISTED = [
    {
        "ID": "broadcasts",
        "ServerID": 123457,
        "Name": "Broadcast Stream",
        "Description": "This is my stream to send broadcast messages",
        "MessageStreamType": "Broadcasts",
        "CreatedAt": "2020-07-01T00:00:00-04:00",
        "UpdatedAt": "2020-07-01T00:00:00-04:00",
        "ArchivedAt": "2020-07-03T00:00:00-04:00",
        "ExpectedPurgeDate": "2020-08-17T00:00:00-04:00",
        "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "Postmark"},
    },
    {
        "ID": "outbound",
        "ServerID": 123457,
        "Name": "Transactional Stream",
        "Description": "This is my stream to send transactional messages",
        "MessageStreamType": "Transactional",
        "CreatedAt": "2020-07-01T00:00:00-04:00",
        "UpdatedAt": "2020-07-05T00:00:00-04:00",
        "ArchivedAt": None,
        "ExpectedPurgeDate": None,
        "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "none"},
    },
]
CREATED = {
    "ID": "transactional-dev",
    "ServerID": 123457,
    "Name": "My Dev Transactional Stream",
    "Description": "This is my second transactional stream",
    "MessageStreamType": "Transactional",
    "CreatedAt": "2020-07-02T00:00:00-04:00",
    "UpdatedAt": "2020-07-02T00:00:00-04:00",
    "ArchivedAt": None,
    "ExpectedPurgeDate": None,
    "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "None"},
}
EDITED = {
    "ID": "transactional-dev",
    "ServerID": 123457,
    "Name": "Updated Dev Stream",
    "Description": "Updating my dev transactional stream",
    "MessageStreamType": "Transactional",
    "CreatedAt": "2020-07-02T00:00:00-04:00",
    "UpdatedAt": "2020-07-03T00:00:00-04:00",
    "ArchivedAt": None,
    "ExpectedPurgeDate": None,
    "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "none"},
}
ARCHIVED = {
    "ID": "transactional-dev",
    "ServerID": 123457,
    "ExpectedPurgeDate": "2020-08-30T12:30:00.00-04:00",
}
UNARCHIVED = {
    "ID": "transactional-dev",
    "ServerID": 123457,
    "Name": "Updated Dev Stream",
    "Description": "Updating my dev transactional stream",
    "MessageStreamType": "Transactional",
    "CreatedAt": "2020-07-02T00:00:00-04:00",
    "UpdatedAt": "2020-07-04T00:00:00-04:00",
    "ArchivedAt": None,
    "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "none"},
}


def assert_request(api_request, method, path, json=None, params=None):
    api_request.assert_called_once_with(
        method,
        f"https://api.postmarkapp.com{path}",
        json=json,
        params=params or {},
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "X-Postmark-Server-Token": "SERVER_TOKEN",
        },
        timeout=30,
    )


@pytest.fixture
def respond(api_request):
    def inner(data):
        api_request.return_value.json.return_value = data

    return inner


@pytest.fixture
def stream(client, flavor):
    return twin(MessageStream, flavor)(manager=client.message_streams, **CREATED)


async def test_manager_registered(client, flavor):
    assert isinstance(client.message_streams, twin(MessageStreamsManager, flavor))


@pytest.mark.parametrize(
    "kwargs, params",
    (
        ({}, {"MessageStreamType": None, "IncludeArchivedStreams": None}),
        (
            {"MessageStreamType": "Broadcasts", "IncludeArchivedStreams": True},
            {"MessageStreamType": "Broadcasts", "IncludeArchivedStreams": True},
        ),
    ),
)
async def test_manager_all(client, flavor, api_request, respond, kwargs, params):
    respond({"MessageStreams": LISTED, "TotalCount": 2})
    streams = await aw(client.message_streams.all(**kwargs))
    assert_request(api_request, "GET", "/message-streams", params=params)
    assert all(isinstance(stream, twin(MessageStream, flavor)) for stream in streams)
    assert [stream.as_dict() for stream in streams] == LISTED
    assert [stream.Name for stream in streams] == ["Broadcast Stream", "Transactional Stream"]


async def test_manager_get(client, flavor, api_request, respond):
    respond(BROADCASTS)
    stream = await aw(client.message_streams.get("broadcasts"))
    assert_request(api_request, "GET", "/message-streams/broadcasts")
    assert isinstance(stream, twin(MessageStream, flavor))
    assert stream.as_dict() == BROADCASTS
    assert stream.SubscriptionManagementConfiguration == {"UnsubscribeHandlingType": "Postmark"}
    assert repr(stream) == f"<{twin(MessageStream, flavor).__name__}: broadcasts>"


async def test_manager_create(client, flavor, api_request, respond):
    respond(CREATED)
    stream = await aw(
        client.message_streams.create(
            ID="transactional-dev",
            Name="My Dev Transactional Stream",
            MessageStreamType="Transactional",
            Description="This is my second transactional stream",
            SubscriptionManagementConfiguration={"UnsubscribeHandlingType": "None"},
        )
    )
    assert_request(
        api_request,
        "POST",
        "/message-streams",
        json={
            "ID": "transactional-dev",
            "Name": "My Dev Transactional Stream",
            "MessageStreamType": "Transactional",
            "Description": "This is my second transactional stream",
            "SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "None"},
        },
    )
    assert isinstance(stream, twin(MessageStream, flavor))
    assert stream.as_dict() == CREATED


async def test_manager_create_omits_unset_optional_fields(client, api_request, respond):
    respond(CREATED)
    await aw(
        client.message_streams.create(
            ID="transactional-dev", Name="My Dev Transactional Stream", MessageStreamType="Transactional"
        )
    )
    assert_request(
        api_request,
        "POST",
        "/message-streams",
        json={
            "ID": "transactional-dev",
            "Name": "My Dev Transactional Stream",
            "MessageStreamType": "Transactional",
        },
    )


@pytest.mark.parametrize(
    "kwargs",
    (
        {"Name": "Updated Dev Stream", "Description": "Updating my dev transactional stream"},
        {"SubscriptionManagementConfiguration": {"UnsubscribeHandlingType": "Custom"}},
    ),
)
async def test_manager_edit(client, flavor, api_request, respond, kwargs):
    respond(EDITED)
    stream = await aw(client.message_streams.edit("transactional-dev", **kwargs))
    assert_request(api_request, "PATCH", "/message-streams/transactional-dev", json=kwargs)
    assert isinstance(stream, twin(MessageStream, flavor))
    assert stream.as_dict() == EDITED


async def test_manager_archive(client, api_request, respond):
    respond(ARCHIVED)
    assert await aw(client.message_streams.archive("transactional-dev")) == ARCHIVED
    assert_request(api_request, "POST", "/message-streams/transactional-dev/archive")


async def test_manager_unarchive(client, flavor, api_request, respond):
    respond(UNARCHIVED)
    stream = await aw(client.message_streams.unarchive("transactional-dev"))
    assert_request(api_request, "POST", "/message-streams/transactional-dev/unarchive")
    assert isinstance(stream, twin(MessageStream, flavor))
    assert stream.as_dict() == UNARCHIVED


async def test_model_str(stream, flavor):
    assert str(stream) == f"{twin(MessageStream, flavor).__name__}: transactional-dev"


async def test_model_get(stream, api_request, respond):
    respond(EDITED)
    assert await aw(stream.get()) is stream
    assert_request(api_request, "GET", "/message-streams/transactional-dev")
    assert stream.as_dict() == EDITED
    assert stream.Name == "Updated Dev Stream"


async def test_model_edit(stream, api_request, respond):
    respond(EDITED)
    assert await aw(stream.edit(Name="Updated Dev Stream")) is None
    assert_request(api_request, "PATCH", "/message-streams/transactional-dev", json={"Name": "Updated Dev Stream"})
    assert stream.as_dict() == EDITED
    assert stream.Name == "Updated Dev Stream"
    assert stream.UpdatedAt == "2020-07-03T00:00:00-04:00"


async def test_model_archive(stream, api_request, respond):
    respond(ARCHIVED)
    assert await aw(stream.archive()) == ARCHIVED
    assert_request(api_request, "POST", "/message-streams/transactional-dev/archive")


async def test_model_unarchive(flavor, stream, api_request, respond):
    respond(UNARCHIVED)
    restored = await aw(stream.unarchive())
    assert_request(api_request, "POST", "/message-streams/transactional-dev/unarchive")
    assert isinstance(restored, twin(MessageStream, flavor))
    assert restored.as_dict() == UNARCHIVED
