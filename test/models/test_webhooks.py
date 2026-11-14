import json

import pytest

from postmarker.models.bounces import Bounce, SpamComplaint
from postmarker.models.messages import OutboundMessage
from postmarker.models.suppressions import SubscriptionChange

from ..conftest import BOUNCE_WEBHOOK, aw, twin

pytestmark = pytest.mark.anyio

API = "https://api.postmarkapp.com"
MESSAGE_ID = "883953f4-6105-42a2-a16a-77a8eac79483"

# https://postmarkapp.com/developer/webhooks/spam-complaint-webhook
SPAM_COMPLAINT_WEBHOOK = """{
  "RecordType": "SpamComplaint",
  "MessageStream": "outbound",
  "ID": 692560174,
  "Type": "SpamComplaint",
  "TypeCode": 100001,
  "Name": "Spam complaint",
  "Tag": "welcome-email",
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "Metadata": {
    "PropA": "some value",
    "PropB": "some value"
  },
  "ServerID": 23,
  "Description": "The subscriber explicitly marked this message as spam.",
  "Details": "Test spam complaint details",
  "Email": "margareth@nasa.com",
  "From": "alanturing@computers.com",
  "BouncedAt": "2026-11-05T16:33:54.9070259Z",
  "DumpAvailable": true,
  "Inactive": true,
  "CanActivate": false,
  "Subject": "Saying Hello!",
  "Content": "<Abuse report dump>"
}"""

# https://postmarkapp.com/developer/webhooks/subscription-change-webhook
SUBSCRIPTION_CHANGE_WEBHOOK = """{
  "RecordType": "SubscriptionChange",
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "ServerID": 23,
  "MessageStream": "outbound",
  "ChangedAt": "2026-11-05T16:33:54.9070259Z",
  "Recipient": "margareth@nasa.com",
  "Origin": "Recipient",
  "SuppressSending": true,
  "SuppressionReason": "HardBounce",
  "Tag": "welcome-email",
  "Metadata": {
    "PropA": "some value",
    "PropB": "some value"
  }
}"""


def test_spam_complaint(client, flavor):
    complaint = client.bounces.SpamComplaint(SPAM_COMPLAINT_WEBHOOK)

    assert type(complaint) is twin(SpamComplaint, flavor)
    assert isinstance(complaint, twin(Bounce, flavor))
    assert complaint._manager is client.bounces
    assert complaint.as_dict() == json.loads(SPAM_COMPLAINT_WEBHOOK)
    assert complaint.Email == "margareth@nasa.com"
    assert str(complaint) == "Spam complaint from margareth@nasa.com"


def test_subscription_change(client, flavor):
    change = client.suppressions.SubscriptionChange(SUBSCRIPTION_CHANGE_WEBHOOK)

    assert type(change) is twin(SubscriptionChange, flavor)
    assert change._manager is client.suppressions
    assert change.as_dict() == json.loads(SUBSCRIPTION_CHANGE_WEBHOOK)
    assert change.SuppressSending is True
    assert change.SuppressionReason == "HardBounce"
    assert str(change) == "Subscription change for margareth@nasa.com"


@pytest.mark.parametrize(
    "parse, attribute, url",
    (
        (
            lambda client: client.bounces.SpamComplaint(SPAM_COMPLAINT_WEBHOOK),
            "message",
            f"{API}/messages/outbound/{MESSAGE_ID}/details",
        ),
        (
            lambda client: client.bounces.SpamComplaint(SPAM_COMPLAINT_WEBHOOK),
            "dump",
            f"{API}/bounces/692560174/dump",
        ),
        (
            lambda client: client.suppressions.SubscriptionChange(SUBSCRIPTION_CHANGE_WEBHOOK),
            "message",
            f"{API}/messages/outbound/{MESSAGE_ID}/details",
        ),
    ),
    ids=("spam-complaint-message", "spam-complaint-dump", "subscription-change-message"),
)
async def test_related_data(client, api_request, parse, attribute, url):
    await aw(getattr(parse(client), attribute))

    assert api_request.call_args.args == ("GET", url)


async def test_webhook_model_message(client, flavor, api_request):
    api_request.return_value.json.return_value = {"MessageID": MESSAGE_ID, "Status": "Sent", "Recipients": []}
    bounce = client.bounces.Bounce(BOUNCE_WEBHOOK)
    assert isinstance(bounce, twin(Bounce, flavor))
    message = await aw(bounce.message)
    assert isinstance(message, twin(OutboundMessage, flavor))
    assert message.MessageID == MESSAGE_ID
