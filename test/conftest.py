import inspect
import os
import sys
import unittest
from contextlib import contextmanager
from unittest.mock import Mock
from urllib.parse import parse_qsl, urlsplit

import httpx2
import pytest
import yaml
from pytest_recording.plugin import get_default_cassette_name

from postmarker.core import AsyncPostmarkClient, PostmarkClient
from postmarker.models.emails import Delivery

DEFAULT_SERVER_TOKEN = "SERVER_TOKEN"
DEFAULT_ACCOUNT_TOKEN = "ACCOUNT_TOKEN"
SERVER_TOKEN = os.environ.get("SERVER_TOKEN", DEFAULT_SERVER_TOKEN)
ACCOUNT_TOKEN = os.environ.get("ACCOUNT_TOKEN", DEFAULT_ACCOUNT_TOKEN)


def pytest_collection_modifyitems(items):
    # unittest classes (e.g. tornado's AsyncHTTPTestCase) are the only allowed ones
    classes = [item.nodeid for item in items if item.cls and not issubclass(item.cls, unittest.TestCase)]
    if classes:
        raise pytest.UsageError("Write test functions, not test classes:\n" + "\n".join(classes))


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(params=["sync", "async"])
def flavor(request):
    return request.param


@pytest.fixture
def api_request(flavor, request):
    return request.getfixturevalue("postmark_request" if flavor == "sync" else "postmark_async_request")


def without_flavor(name):
    """Drops the `sync` / `async` parameter id, so both flavors share today's cassette names."""
    if "[" not in name:
        return name
    base, ids = name[:-1].split("[", 1)
    ids = "-".join(part for part in ids.split("-") if part not in ("sync", "async"))
    return f"{base}[{ids}]" if ids else base


@pytest.fixture
def default_cassette_name(request):
    marker = request.node.get_closest_marker("default_cassette")
    if marker is not None:
        return marker.args[0]
    return get_default_cassette_name(request.cls, without_flavor(request.node.name))


def request_key(method, url):
    parts = urlsplit(str(url))
    return method, parts.path, sorted(parse_qsl(parts.query, keep_blank_values=True))


def CassetteTransport(path):
    """Replays a vcr cassette for the async client, in recording order."""
    with open(path) as fd:
        pending = iter(yaml.safe_load(fd)["interactions"])

    def handler(request):
        interaction = next(pending, None)
        assert interaction is not None, f"No recorded interaction left for {request.method} {request.url}"
        recorded = request_key(interaction["request"]["method"], interaction["request"]["uri"])
        assert request_key(request.method, request.url) == recorded, f"{request.method} {request.url} != {recorded}"
        response = interaction["response"]
        body = response["body"]["string"]
        headers = {name: values[0] for name, values in response["headers"].items() if name.lower() == "content-type"}
        return httpx2.Response(
            response["status"]["code"], content=body if isinstance(body, bytes) else body.encode(), headers=headers
        )

    return httpx2.MockTransport(handler)


def no_network(request):
    raise AssertionError(f"No cassette for {request.method} {request.url}")


@pytest.fixture
def client(flavor, server_token, account_token, vcr_cassette_dir, default_cassette_name):
    if flavor == "sync":
        return PostmarkClient(server_token=server_token, account_token=account_token)
    client = AsyncPostmarkClient(server_token=server_token, account_token=account_token)
    path = os.path.join(vcr_cassette_dir, f"{default_cassette_name}.yaml")
    client._transport = CassetteTransport(path) if os.path.exists(path) else httpx2.MockTransport(no_network)
    return client


async def aw(value):
    return await value if inspect.isawaitable(value) else value


def twin(cls, flavor):
    return cls if flavor == "sync" else getattr(sys.modules[cls.__module__], f"Async{cls.__name__}")


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [
            ("X-Postmark-Server-Token", DEFAULT_SERVER_TOKEN),
            ("X-Postmark-Account-Token", DEFAULT_ACCOUNT_TOKEN),
        ],
        "decode_compressed_response": True,
    }


@pytest.fixture(scope="session")
def server_token():
    return SERVER_TOKEN


@pytest.fixture(scope="session")
def account_token():
    return ACCOUNT_TOKEN


@pytest.fixture(scope="session")
def postmark(server_token, account_token):
    return PostmarkClient(server_token=server_token, account_token=account_token)


@pytest.fixture
def bounce(postmark):
    return postmark.bounces.get(723626745)


@pytest.fixture
def server(postmark):
    return postmark.server.get()


@pytest.fixture
def email(postmark):
    return postmark.emails.Email(From="sender@example.com", To="receiver@example.com", TextBody="text")


@pytest.fixture
def email_template(postmark):
    return postmark.emails.EmailTemplate(
        From="sender@example.com", To="receiver@example.com", TemplateId=983381, TemplateModel={}
    )


@pytest.fixture
def email_batch(postmark, email):
    return postmark.emails.EmailBatch(email)


@pytest.fixture
def email_template_batch(postmark, email):
    return postmark.emails.EmailTemplateBatch(email)


@pytest.fixture
def template(postmark):
    return postmark.templates.get(983381)


@pytest.fixture
def domain(postmark):
    return postmark.domains.get(64054)


@pytest.fixture
def outbound_message(postmark):
    return postmark.messages.outbound.all(count=1)[0]


@contextmanager
def _catch_signal(signal):
    handler = Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)


@pytest.fixture
def catch_signal():
    return _catch_signal


BOUNCE_WEBHOOK = """{
  "ID": 42,
  "Type": "HardBounce",
  "TypeCode": 1,
  "Name": "Hard bounce",
  "Tag": "Test",
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "ServerId": 23,
  "Description": "The server was unable to deliver your message (ex: unknown user, mailbox not found).",
  "Details": "Test bounce details",
  "Email": "john@example.com",
  "From": "sender@example.com",
  "BouncedAt": "2014-08-01T13:28:10.2735393-04:00",
  "DumpAvailable": true,
  "Inactive": true,
  "CanActivate": true,
  "Subject": "Test subject"
}"""


@pytest.fixture
def bounce_webhook(postmark):
    return postmark.bounces.Bounce(json=BOUNCE_WEBHOOK)


OPEN_WEBHOOK = """{
  "FirstOpen": true,
  "Client": {
    "Name": "Chrome 35.0.1916.153",
    "Company": "Google",
    "Family": "Chrome"
  },
  "OS": {
    "Name": "OS X 10.7 Lion",
    "Company": "Apple Computer, Inc.",
    "Family": "OS X 10"
  },
  "Platform": "WebMail",
  "UserAgent": "Some UA string",
  "ReadSeconds": 5,
  "Geo": {
    "CountryISOCode": "RS",
    "Country": "Serbia",
    "RegionISOCode": "VO",
    "Region": "Autonomna Pokrajina Vojvodina",
    "City": "Novi Sad",
    "Zip": "21000",
    "Coords": "45.2517,19.8369",
    "IP": "188.2.95.4"
  },
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "ReceivedAt": "2014-06-01T12:00:00",
  "Tag": "welcome-email",
  "Recipient": "john@example.com"
}"""


@pytest.fixture
def open_webhook(postmark):
    return postmark.messages.outbound.opens.Open(json=OPEN_WEBHOOK)


INBOUND_WEBHOOK = """{
"BccFull": [
  {"MailboxHash": "", "Name": "First Bcc", "Email": "firstbcc@postmarkapp.com"},
  {"MailboxHash": "", "Name": "", "Email": "secondbcc@postmarkapp.com"}
],
"Tag": "TestTag",
"StrippedTextReply": "This is the reply text",
"FromFull": {"MailboxHash": "", "Name": "Postmarkapp Support", "Email": "support@postmarkapp.com"},
"CcFull": [
  {"MailboxHash": "", "Name": "First Cc", "Email": "firstcc@postmarkapp.com"},
  {"MailboxHash": "", "Name": "", "Email": "secondCc@postmarkapp.com"}
],
"Cc": "\\"First Cc\\" <firstcc@postmarkapp.com>, secondCc@postmarkapp.com>",
"To": "\\"Firstname Lastname\\" <yourhash+SampleHash@inbound.postmarkapp.com>",
"Attachments": [
  {
    "ContentType": "text/plain",
    "Name": "test.txt",
    "ContentLength": 45,
    "Content": "VGhpcyBpcyBhdHRhY2htZW50IGNvbnRlbnRzLCBiYXNlLTY0IGVuY29kZWQu"
  }
],
"From": "support@postmarkapp.com",
"FromName": "Postmarkapp Support",
"Date": "Fri, 1 Aug 2014 16:45:32 -04:00",
"MessageID": "73e6d360-66eb-11e1-8e72-a8904824019b",
"TextBody": "This is a test text body.",
"ToFull": [
  {"MailboxHash": "SampleHash", "Name": "Firstname Lastname", "Email": "yourhash+SampleHash@inbound.postmarkapp.com"}
],
"HtmlBody": "<html><body><p>This is a test html body.<\\\\/p><\\\\/body><\\\\/html>",
"MailboxHash": "SampleHash",
"Headers": [
  {"Name": "X-Header-Test", "Value": ""},
  {"Name": "X-Spam-Status", "Value": "No"},
  {"Name": "X-Spam-Score", "Value": "-0.1"},
  {"Name": "X-Spam-Tests", "Value": "DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,SPF_PASS"}
],
"ReplyTo": "replyto@postmarkapp.com",
"Subject": "Test subject",
"OriginalRecipient": "yourhash+SampleHash@inbound.postmarkapp.com",
"Bcc": "\\"First Bcc\\" <firstbcc@postmarkapp.com>, secondbcc@postmarkapp.com>"
}"""


@pytest.fixture
def inbound_webhook(postmark):
    return postmark.messages.inbound.InboundMessage(INBOUND_WEBHOOK)


@pytest.fixture
def attachment(inbound_webhook):
    return inbound_webhook.Attachments[0]


DELIVERY_WEBHOOK = """{
  "ServerId": 23,
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "Recipient": "john@example.com",
  "Tag": "welcome-email",
  "DeliveredAt": "2014-08-01T13:28:10.2735393-04:00",
  "Details": "Test delivery webhook details"
}"""


@pytest.fixture
def delivery_webhook():
    return Delivery.from_json(DELIVERY_WEBHOOK)
