from contextlib import contextmanager
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from unittest.mock import patch

import pytest

from postmarker.exceptions import ClientError
from postmarker.models.base import ModelManager
from postmarker.models.emails import deconstruct_multipart
from postmarker.models.messages import Attachment, InboundMessage, Open, OutboundMessage

pytestmark = pytest.mark.vcr


def test_sub_managers(postmark):
    outbound = postmark.messages.outbound
    assert isinstance(outbound, ModelManager)
    assert outbound.client is postmark

    inbound = postmark.messages.inbound
    assert isinstance(inbound, ModelManager)
    assert inbound.client is postmark

    opens = postmark.messages.outbound.opens
    assert isinstance(opens, ModelManager)
    assert opens.client is postmark


@contextmanager
def not_found(message="[701] This message was not found."):
    with pytest.raises(ClientError) as exc:
        yield
    assert str(exc.value) == message


def test_outbound_message(outbound_message):
    assert isinstance(outbound_message, OutboundMessage)
    assert str(outbound_message) == "Sent message to test@example.com"


def test_outbound_message_get(outbound_message):
    assert outbound_message.get().Body == "Body example"


def test_outbound_message_get_dump(outbound_message):
    assert outbound_message.get_dump() == "Body example"


def test_outbound_message_opens(outbound_message):
    with not_found():
        outbound_message.opens()


@pytest.fixture
def inbound_message(postmark):
    return InboundMessage(
        postmark.messages.inbound,
        MessageID="123",
        Status="Blocked",
        From="test@example.com",
    )


def test_inbound_message(inbound_message):
    assert isinstance(inbound_message, InboundMessage)
    assert str(inbound_message) == "Blocked message from test@example.com"


def test_inbound_message_get(inbound_message):
    with patch.object(inbound_message._manager, "call", return_value=inbound_message.as_dict()):
        instance = inbound_message.get()
    assert isinstance(instance, InboundMessage)


def test_inbound_message_bypass(inbound_message):
    with not_found("[701] This message was not found or cannot be bypassed."):
        inbound_message.bypass()


def test_inbound_message_retry(inbound_message):
    with not_found("[701] This message was not found or cannot be retried."):
        inbound_message.retry()


def test_inbound_messages_all(postmark):
    assert postmark.messages.inbound.all() == []


def test_inbound_message_headers(inbound_webhook):
    assert inbound_webhook["X-Spam-Status"] == "No"


def test_inbound_message_not_existing_header(inbound_webhook):
    with pytest.raises(KeyError):
        assert inbound_webhook["Unknown"]


@pytest.fixture
def inbound_mime(inbound_webhook):
    del inbound_webhook._data["MessageID"]
    del inbound_webhook.__dict__["MessageID"]
    return inbound_webhook.as_mime()


def test_inbound_as_mime_type(inbound_mime):
    assert isinstance(inbound_mime, MIMEMultipart)


def test_inbound_as_mime_headers(inbound_mime):
    assert inbound_mime["X-Spam-Status"] == "No"
    assert inbound_mime["Subject"] == "Test subject"
    assert inbound_mime["From"] == "support@postmarkapp.com"
    assert inbound_mime["To"] == '"Firstname Lastname" <yourhash+SampleHash@inbound.postmarkapp.com>'
    assert "MessageID" not in inbound_mime


def test_inbound_as_mime_text_content(inbound_mime):
    text, _, _ = deconstruct_multipart(inbound_mime)
    assert text == "This is a test text body."


def test_inbound_as_mime_html_content(inbound_mime):
    _, html, _ = deconstruct_multipart(inbound_mime)
    assert html == r"<html><body><p>This is a test html body.<\/p><\/body><\/html>"


def test_inbound_as_mime_attachment(inbound_mime):
    _, _, attachments = deconstruct_multipart(inbound_mime)
    assert len(attachments) == 1
    attachment = attachments[0]
    assert isinstance(attachment, MIMEBase)
    assert attachment["Content-Type"] == "text/plain"
    assert attachment["Content-Transfer-Encoding"] == "base64"
    assert attachment["Content-Disposition"] == 'attachment; filename="test.txt"'
    assert attachment.get_payload(decode=True) == b"This is attachment contents, base-64 encoded."


def test_attachment_instance(attachment):
    assert isinstance(attachment, Attachment)


def test_attachment_repr(attachment):
    assert repr(attachment) == "<Attachment: test.txt>"


def test_attachment_len(attachment):
    assert len(attachment) == 45


@pytest.mark.parametrize("attribute", ("ContentType", "Name", "ContentLength", "Content"))
def test_attachment_attributes(attachment, attribute):
    assert getattr(attachment, attribute) == attachment._data[attribute]


def test_attachment_save(attachment, tmpdir):
    filename = tmpdir.join(attachment.Name)
    assert attachment.save(str(tmpdir)) == filename
    with filename.open() as fd:
        assert fd.read() == "This is attachment contents, base-64 encoded."


def test_attachment_as_mime(attachment):
    message = attachment.as_mime()
    assert isinstance(message, MIMEBase)
    assert message["Content-Type"] == attachment.ContentType
    assert message["Content-Transfer-Encoding"] == "base64"
    assert message["Content-Disposition"] == 'attachment; filename="test.txt"'
    assert message.get_payload(decode=True) == b"This is attachment contents, base-64 encoded."


def test_opens_model(postmark):
    open = postmark.messages.outbound.opens.all(count=1)[0]
    assert isinstance(open, Open)
    assert str(open) == "Open from test@example.com"


def test_opens_webhook(open_webhook):
    assert isinstance(open_webhook, Open)
    assert str(open_webhook) == "Open from john@example.com"
