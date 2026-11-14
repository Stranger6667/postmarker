import json

import pytest
from requests import Request

from postmarker.core import USER_AGENT
from postmarker.models.messages import Click, ClicksManager, OutboundMessage

from ..conftest import aw, twin

pytestmark = pytest.mark.anyio

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


async def test_manager(client, flavor):
    clicks = client.messages.outbound.clicks
    assert isinstance(clicks, twin(ClicksManager, flavor))
    assert clicks.client is client
    assert repr(clicks) == f"<{twin(ClicksManager, flavor).__name__}>"


async def test_all(client, flavor, api_request):
    api_request.return_value.json.return_value = CLICKS

    clicks = await aw(client.messages.outbound.clicks.all())

    api_request.assert_called_once_with(
        "GET",
        "https://api.postmarkapp.com/messages/outbound/clicks",
        json=None,
        params={"count": 500, "offset": 0, **NO_FILTERS},
        headers=HEADERS,
        timeout=None,
    )
    assert len(clicks) == 1
    click = clicks[0]
    assert isinstance(click, twin(Click, flavor))
    assert click.as_dict() == CLICK
    assert str(click) == "Click from john.doe@yahoo.com"
    assert click.ClickLocation == "HTML"
    assert click.OriginalLink == "https://example.com"


async def test_all_filters(client, api_request):
    api_request.return_value.json.return_value = CLICKS

    await aw(
        client.messages.outbound.clicks.all(
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
    )

    method, url = api_request.call_args[0]
    params = api_request.call_args[1]["params"]
    assert Request(method, url, params=params).prepare().url == (
        "https://api.postmarkapp.com/messages/outbound/clicks"
        "?recipient=john.doe%40yahoo.com&tag=welcome-user"
        "&client_name=Chrome+34.0.1847.131&client_company=Google+Inc.&client_family=Chrome"
        "&os_name=OS+X+10.7+Lion&os_family=OS+X&os_company=Apple+Computer%2C+Inc."
        "&platform=WebMail&country=Serbia&region=Autonomna+Pokrajina+Vojvodina&city=Novi+Sad"
        "&messagestream=broadcast&count=50&offset=10"
    )


async def test_all_pages(client, api_request):
    second = {**CLICK, "Recipient": "jane.doe@yahoo.com"}
    api_request.return_value.json.side_effect = [
        {"TotalCount": 501, "Clicks": [CLICK]},
        {"TotalCount": 501, "Clicks": [second]},
    ]

    clicks = await aw(client.messages.outbound.clicks.all(count=None))

    pages = [(call[1]["params"]["count"], call[1]["params"]["offset"]) for call in api_request.call_args_list]
    assert pages == [(500, 0), (500, 500)]
    assert [click.as_dict() for click in clicks] == [CLICK, second]


async def test_get(client, api_request):
    api_request.return_value.json.return_value = CLICKS

    response = await aw(client.messages.outbound.clicks.get(MESSAGE_ID, count=10, offset=5))

    api_request.assert_called_once_with(
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
async def test_outbound_message_clicks(client, flavor, api_request, kwargs, params):
    api_request.return_value.json.return_value = CLICKS
    message = twin(OutboundMessage, flavor)(client.messages.outbound, MessageID=MESSAGE_ID)

    assert await aw(message.clicks(**kwargs)) == CLICKS

    api_request.assert_called_once_with(
        "GET",
        f"https://api.postmarkapp.com/messages/outbound/clicks/{MESSAGE_ID}",
        json=None,
        params=params,
        headers=HEADERS,
        timeout=None,
    )


async def test_click_message(client, flavor, api_request):
    api_request.return_value.json.return_value = CLICKS
    click = (await aw(client.messages.outbound.clicks.all()))[0]
    api_request.reset_mock()
    api_request.return_value.json.return_value = {"MessageID": MESSAGE_ID, "Status": "Sent", "Recipients": []}

    message = await aw(click.message)

    api_request.assert_called_once_with(
        "GET",
        f"https://api.postmarkapp.com/messages/outbound/{MESSAGE_ID}/details",
        json=None,
        params={},
        headers=HEADERS,
        timeout=None,
    )
    assert isinstance(message, twin(OutboundMessage, flavor))
    assert message.MessageID == MESSAGE_ID


async def test_webhook(client, flavor):
    click = client.messages.outbound.clicks.Click(CLICK_WEBHOOK)

    assert isinstance(click, twin(Click, flavor))
    assert str(click) == "Click from margareth@nasa.com"
    assert click.as_dict() == json.loads(CLICK_WEBHOOK)
    assert click.RecordType == "Click"
    assert click.ClickLocation == "HTML"
    assert click.OriginalLink == "https://example.com/confirm-your-address"
    assert click.MessageID == "883953f4-6105-42a2-a16a-77a8eac79483"
    assert click.Metadata == {"PropA": "some value", "PropB": "some value"}
    assert click.Geo["City"] == "Houston"
