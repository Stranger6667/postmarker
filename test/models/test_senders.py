from unittest.mock import call

import pytest

from postmarker.core import USER_AGENT
from postmarker.exceptions import ClientError
from postmarker.models.senders import SenderSignature

pytestmark = pytest.mark.vcr


def test_all(postmark):
    sender_signature = postmark.senders.all(1)[0]
    assert isinstance(sender_signature, SenderSignature)


def test_get(postmark):
    sender_signature = postmark.senders.get(128462)
    assert isinstance(sender_signature, SenderSignature)
    data = sender_signature.as_dict()
    new_data = sender_signature.get().as_dict()
    assert data == new_data


def test_edit(postmark):
    sender_signature = postmark.senders.get(128462)
    sender_signature.edit(Name="Test")
    assert sender_signature.Name == "Test"


def test_all_methods(postmark):
    new_signature = postmark.senders.create("exampleX@blablaz.com", "Test")
    assert new_signature.resend() == "Confirmation email for Sender Signature exampleX@blablaz.com was re-sent."
    assert new_signature.verifyspf() == {
        "Confirmed": False,
        "DKIMHost": "",
        "DKIMPendingTextValue": "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXFLm6c/taesECCj3KSbNrefbtl0tJHC6W3J"
        "XysuB0CT4jOP52/398yqaNZ1KyuAodVl/wZzSD7yJrP+cHsjgpXgDzMu7ShpZTtmMpaApfAQhgLPXcLaYE0"
        "xX72/95XdaZHixIWkvv3I1U7Ls9WJEZif7ZSpl61d9jfIE77G3AhQIDAQAB",
        "DKIMPendingHost": "20170204193206pm._domainkey.blablaz.com",
        "DKIMRevokedHost": "",
        "DKIMRevokedTextValue": "",
        "DKIMTextValue": "",
        "DKIMUpdateStatus": "Pending",
        "DKIMVerified": False,
        "Domain": "blablaz.com",
        "EmailAddress": "exampleX@blablaz.com",
        "ID": 723694,
        "Name": "Test",
        "ReplyToEmailAddress": "",
        "ReturnPathDomain": "",
        "ReturnPathDomainCNAMEValue": "pm.mtasv.net",
        "ReturnPathDomainVerified": False,
        "SPFHost": "blablaz.com",
        "SPFTextValue": "v=spf1 a mx include:spf.mtasv.net ~all",
        "SPFVerified": False,
        "SafeToRemoveRevokedKeyFromDNS": False,
        "WeakDKIM": False,
    }
    with pytest.deprecated_call(), pytest.raises(ClientError) as exc:
        new_signature.requestnewdkim()
    assert str(exc.value) == "[505] This DKIM is already being renewed."
    assert new_signature.delete() == "Signature exampleX@blablaz.com removed."


ACCOUNT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
    "X-Postmark-Account-Token": "ACCOUNT_TOKEN",
}
NOTE = "This is a note visible to the recipient to provide context of what Postmark is."


@pytest.mark.parametrize("note", ({}, {"ConfirmationPersonalNote": NOTE}))
def test_create_confirmation_personal_note(postmark_client, postmark_request, note):
    postmark_request.return_value.json.return_value = {"ID": 1, "Name": "John Doe"}
    postmark_client.senders.create("john.doe@example.com", "John Doe", **note)
    assert postmark_request.call_args == call(
        "POST",
        "https://api.postmarkapp.com/senders/",
        json={
            "FromEmail": "john.doe@example.com",
            "Name": "John Doe",
            "ReplyToEmail": None,
            "ReturnPathDomain": None,
            **note,
        },
        params={},
        headers=ACCOUNT_HEADERS,
        timeout=None,
    )


@pytest.mark.parametrize("note", ({}, {"ConfirmationPersonalNote": NOTE}))
def test_edit_confirmation_personal_note(postmark_client, postmark_request, note):
    postmark_request.return_value.json.return_value = {"ID": 1, "Name": "John Doe"}
    postmark_client.senders.edit(1, "John Doe", **note)
    assert postmark_request.call_args == call(
        "PUT",
        "https://api.postmarkapp.com/senders/1",
        json={"Name": "John Doe", "ReplyToEmail": None, "ReturnPathDomain": None, **note},
        params={},
        headers=ACCOUNT_HEADERS,
        timeout=None,
    )
