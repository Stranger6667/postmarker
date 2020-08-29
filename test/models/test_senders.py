import pytest

from postmarker.exceptions import ClientError
from postmarker.models.senders import SenderSignature

CASSETTE_NAME = "senders"


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
