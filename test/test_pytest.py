import pytest

from postmarker.core import PostmarkClient


def test_postmark_client(postmark_client, postmark_request):
    assert isinstance(postmark_client, PostmarkClient)
    assert postmark_client.mock is postmark_request


def test_return_value_configurable(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {"ID": 1}
    assert postmark_client.call("GET", "/server") == {"ID": 1}


def test_payload_still_serialized(postmark_client):
    with pytest.raises(Exception, match="not JSON serializable"):
        postmark_client.call("POST", "/email", data={"Metadata": object()})
