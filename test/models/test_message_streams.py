import pytest

from postmarker.core import USER_AGENT
from postmarker.models.message_streams import MessageStream, MessageStreamsManager

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


def assert_request(postmark_request, method, path, json=None, params=None):
    postmark_request.assert_called_once_with(
        method,
        f"https://api.postmarkapp.com{path}",
        json=json,
        params=params or {},
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "X-Postmark-Server-Token": "SERVER_TOKEN",
        },
        timeout=None,
    )


@pytest.fixture
def respond(postmark_request):
    def inner(data):
        postmark_request.return_value.json.return_value = data

    return inner


@pytest.fixture
def stream(postmark_client):
    return MessageStream(manager=postmark_client.message_streams, **CREATED)


class TestManager:
    def test_registered(self, postmark_client):
        assert isinstance(postmark_client.message_streams, MessageStreamsManager)

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
    def test_all(self, postmark_client, postmark_request, respond, kwargs, params):
        respond({"MessageStreams": LISTED, "TotalCount": 2})
        streams = postmark_client.message_streams.all(**kwargs)
        assert_request(postmark_request, "GET", "/message-streams", params=params)
        assert all(isinstance(stream, MessageStream) for stream in streams)
        assert [stream.as_dict() for stream in streams] == LISTED
        assert [stream.Name for stream in streams] == ["Broadcast Stream", "Transactional Stream"]

    def test_get(self, postmark_client, postmark_request, respond):
        respond(BROADCASTS)
        stream = postmark_client.message_streams.get("broadcasts")
        assert_request(postmark_request, "GET", "/message-streams/broadcasts")
        assert isinstance(stream, MessageStream)
        assert stream.as_dict() == BROADCASTS
        assert stream.SubscriptionManagementConfiguration == {"UnsubscribeHandlingType": "Postmark"}
        assert repr(stream) == "<MessageStream: broadcasts>"

    def test_create(self, postmark_client, postmark_request, respond):
        respond(CREATED)
        stream = postmark_client.message_streams.create(
            ID="transactional-dev",
            Name="My Dev Transactional Stream",
            MessageStreamType="Transactional",
            Description="This is my second transactional stream",
            SubscriptionManagementConfiguration={"UnsubscribeHandlingType": "None"},
        )
        assert_request(
            postmark_request,
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
        assert isinstance(stream, MessageStream)
        assert stream.as_dict() == CREATED

    def test_create_omits_unset_optional_fields(self, postmark_client, postmark_request, respond):
        respond(CREATED)
        postmark_client.message_streams.create(
            ID="transactional-dev", Name="My Dev Transactional Stream", MessageStreamType="Transactional"
        )
        assert_request(
            postmark_request,
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
    def test_edit(self, postmark_client, postmark_request, respond, kwargs):
        respond(EDITED)
        stream = postmark_client.message_streams.edit("transactional-dev", **kwargs)
        assert_request(postmark_request, "PATCH", "/message-streams/transactional-dev", json=kwargs)
        assert isinstance(stream, MessageStream)
        assert stream.as_dict() == EDITED

    def test_archive(self, postmark_client, postmark_request, respond):
        respond(ARCHIVED)
        assert postmark_client.message_streams.archive("transactional-dev") == ARCHIVED
        assert_request(postmark_request, "POST", "/message-streams/transactional-dev/archive")

    def test_unarchive(self, postmark_client, postmark_request, respond):
        respond(UNARCHIVED)
        stream = postmark_client.message_streams.unarchive("transactional-dev")
        assert_request(postmark_request, "POST", "/message-streams/transactional-dev/unarchive")
        assert isinstance(stream, MessageStream)
        assert stream.as_dict() == UNARCHIVED


class TestModel:
    def test_str(self, stream):
        assert str(stream) == "MessageStream: transactional-dev"

    def test_get(self, stream, postmark_request, respond):
        respond(EDITED)
        assert stream.get() is stream
        assert_request(postmark_request, "GET", "/message-streams/transactional-dev")
        assert stream.as_dict() == EDITED
        assert stream.Name == "Updated Dev Stream"

    def test_edit(self, stream, postmark_request, respond):
        respond(EDITED)
        assert stream.edit(Name="Updated Dev Stream") is None
        assert_request(
            postmark_request, "PATCH", "/message-streams/transactional-dev", json={"Name": "Updated Dev Stream"}
        )
        assert stream.as_dict() == EDITED
        assert stream.Name == "Updated Dev Stream"
        assert stream.UpdatedAt == "2020-07-03T00:00:00-04:00"

    def test_archive(self, stream, postmark_request, respond):
        respond(ARCHIVED)
        assert stream.archive() == ARCHIVED
        assert_request(postmark_request, "POST", "/message-streams/transactional-dev/archive")

    def test_unarchive(self, stream, postmark_request, respond):
        respond(UNARCHIVED)
        restored = stream.unarchive()
        assert_request(postmark_request, "POST", "/message-streams/transactional-dev/unarchive")
        assert isinstance(restored, MessageStream)
        assert restored.as_dict() == UNARCHIVED
