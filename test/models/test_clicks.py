import json

import pytest
from requests import Request

from postmarker.core import USER_AGENT
from postmarker.models.messages import Click, ClicksManager, OutboundMessage

HEADERS = {
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
    "X-Postmark-Server-Token": "SERVER_TOKEN",
}
MESSAGE_ID = "927e56d4-dc66-4070-bbf0-1db76c2ae14b"
# Response shapes from https://postmarkapp.com/developer/api/messages-api#message-clicks
CLICK = {
    "RecordType": "Click",
    "ClickLocation": "HTML",
    "Client": {"Name": "Chrome 34.0.1847.131", "Company": "Google Inc.", "Family": "Chrome"},
    "OS": {"Name": "OS X 10.7 Lion", "Company": "Apple Computer, Inc.", "Family": "OS X"},
    "Platform": "WebMail",
    "UserAgent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/34.0.1847.131 Safari/537.36"
    ),
    "OriginalLink": "https://example.com",
    "Geo": {
        "CountryISOCode": "RS",
        "Country": "Serbia",
        "RegionISOCode": "VO",
        "Region": "Autonomna Pokrajina Vojvodina",
        "City": "Novi Sad",
        "Zip": "21000",
        "Coords": "45.2517,19.8369",
        "IP": "188.2.95.4",
    },
    "MessageID": MESSAGE_ID,
    "MessageStream": "Outbound",
    "ReceivedAt": "2014-04-30T05:04:23.8768746-04:00",
    "Tag": "welcome-user",
    "Recipient": "john.doe@yahoo.com",
}
CLICKS = {"TotalCount": 1, "Clicks": [CLICK]}
NO_FILTERS = {
    "recipient": None,
    "tag": None,
    "client_name": None,
    "client_company": None,
    "client_family": None,
    "os_name": None,
    "os_family": None,
    "os_company": None,
    "platform": None,
    "country": None,
    "region": None,
    "city": None,
    "messagestream": None,
}
# Example event from https://postmarkapp.com/developer/webhooks/click-webhook
CLICK_WEBHOOK = """{
  "RecordType": "Click",
  "MessageStream": "outbound",
  "ClickLocation": "HTML",
  "Client": {
    "Name": "Chrome 140.0.7339.80",
    "Company": "Google",
    "Family": "Chrome"
  },
  "OS": {
    "Name": "macOS 26 Tahoe",
    "Company": "Apple Computer, Inc.",
    "Family": "macOS"
  },
  "Platform": "Desktop",
  "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.80 Safari/537.36",
  "OriginalLink": "https://example.com/confirm-your-address",
  "Geo": {
    "CountryISOCode": "US",
    "Country": "United States",
    "RegionISOCode": "TX",
    "Region": "Texas",
    "City": "Houston",
    "Zip": "77058",
    "Coords": "29.5502,-95.0973",
    "IP": "203.0.113.42"
  },
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "Metadata": {
    "PropA": "some value",
    "PropB": "some value"
  },
  "ReceivedAt": "2026-11-05T16:33:54.9070259Z",
  "Tag": "welcome-email",
  "Recipient": "margareth@nasa.com"
}"""


def test_manager(postmark_client):
    clicks = postmark_client.messages.outbound.clicks
    assert isinstance(clicks, ClicksManager)
    assert clicks.client is postmark_client
    assert repr(clicks) == "<ClicksManager>"


def test_all(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = CLICKS

    clicks = postmark_client.messages.outbound.clicks.all()

    postmark_request.assert_called_once_with(
        "GET",
        "https://api.postmarkapp.com/messages/outbound/clicks",
        json=None,
        params={"count": 500, "offset": 0, **NO_FILTERS},
        headers=HEADERS,
        timeout=None,
    )
    assert len(clicks) == 1
    click = clicks[0]
    assert isinstance(click, Click)
    assert click.as_dict() == CLICK
    assert str(click) == "Click from john.doe@yahoo.com"
    assert click.ClickLocation == "HTML"
    assert click.OriginalLink == "https://example.com"


def test_all_filters(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = CLICKS

    postmark_client.messages.outbound.clicks.all(
        count=50,
        offset=10,
        recipient="john.doe@yahoo.com",
        tag="welcome-user",
        client_name="Chrome 34.0.1847.131",
        client_company="Google Inc.",
        client_family="Chrome",
        os_name="OS X 10.7 Lion",
        os_family="OS X",
        os_company="Apple Computer, Inc.",
        platform="WebMail",
        country="Serbia",
        region="Autonomna Pokrajina Vojvodina",
        city="Novi Sad",
        messagestream="broadcast",
    )

    method, url = postmark_request.call_args[0]
    params = postmark_request.call_args[1]["params"]
    assert Request(method, url, params=params).prepare().url == (
        "https://api.postmarkapp.com/messages/outbound/clicks"
        "?recipient=john.doe%40yahoo.com&tag=welcome-user"
        "&client_name=Chrome+34.0.1847.131&client_company=Google+Inc.&client_family=Chrome"
        "&os_name=OS+X+10.7+Lion&os_family=OS+X&os_company=Apple+Computer%2C+Inc."
        "&platform=WebMail&country=Serbia&region=Autonomna+Pokrajina+Vojvodina&city=Novi+Sad"
        "&messagestream=broadcast&count=50&offset=10"
    )


def test_all_pages(postmark_client, postmark_request):
    second = {**CLICK, "Recipient": "jane.doe@yahoo.com"}
    postmark_request.return_value.json.side_effect = [
        {"TotalCount": 501, "Clicks": [CLICK]},
        {"TotalCount": 501, "Clicks": [second]},
    ]

    clicks = postmark_client.messages.outbound.clicks.all(count=None)

    pages = [(call[1]["params"]["count"], call[1]["params"]["offset"]) for call in postmark_request.call_args_list]
    assert pages == [(500, 0), (500, 500)]
    assert [click.as_dict() for click in clicks] == [CLICK, second]


def test_get(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = CLICKS

    response = postmark_client.messages.outbound.clicks.get(MESSAGE_ID, count=10, offset=5)

    postmark_request.assert_called_once_with(
        "GET",
        f"https://api.postmarkapp.com/messages/outbound/clicks/{MESSAGE_ID}",
        json=None,
        params={"count": 10, "offset": 5},
        headers=HEADERS,
        timeout=None,
    )
    assert response == CLICKS


@pytest.mark.parametrize(
    "kwargs, params",
    (
        ({}, {"count": 500, "offset": 0}),
        ({"count": 10, "offset": 5}, {"count": 10, "offset": 5}),
    ),
)
def test_outbound_message_clicks(postmark_client, postmark_request, kwargs, params):
    postmark_request.return_value.json.return_value = CLICKS
    message = OutboundMessage(postmark_client.messages.outbound, MessageID=MESSAGE_ID)

    assert message.clicks(**kwargs) == CLICKS

    postmark_request.assert_called_once_with(
        "GET",
        f"https://api.postmarkapp.com/messages/outbound/clicks/{MESSAGE_ID}",
        json=None,
        params=params,
        headers=HEADERS,
        timeout=None,
    )


def test_click_message(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = CLICKS
    click = postmark_client.messages.outbound.clicks.all()[0]
    postmark_request.reset_mock()
    postmark_request.return_value.json.return_value = {"MessageID": MESSAGE_ID, "Status": "Sent", "Recipients": []}

    message = click.message

    postmark_request.assert_called_once_with(
        "GET",
        f"https://api.postmarkapp.com/messages/outbound/{MESSAGE_ID}/details",
        json=None,
        params={},
        headers=HEADERS,
        timeout=None,
    )
    assert isinstance(message, OutboundMessage)
    assert message.MessageID == MESSAGE_ID


def test_webhook(postmark_client):
    click = postmark_client.messages.outbound.clicks.Click(CLICK_WEBHOOK)

    assert isinstance(click, Click)
    assert str(click) == "Click from margareth@nasa.com"
    assert click.as_dict() == json.loads(CLICK_WEBHOOK)
    assert click.RecordType == "Click"
    assert click.ClickLocation == "HTML"
    assert click.OriginalLink == "https://example.com/confirm-your-address"
    assert click.MessageID == "883953f4-6105-42a2-a16a-77a8eac79483"
    assert click.Metadata == {"PropA": "some value", "PropB": "some value"}
    assert click.Geo["City"] == "Houston"
