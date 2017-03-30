# coding: utf-8
from contextlib import contextmanager
from email.mime.base import MIMEBase

import pytest

from postmarker.exceptions import ClientError
from postmarker.models.base import ModelManager
from postmarker.models.messages import Attachment, InboundMessage, Open, OutboundMessage


CASSETTE_NAME = 'messages'


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
def not_found(message='[701] This message was not found.'):
    with pytest.raises(ClientError) as exc:
        yield
    assert str(exc.value) == message


class TestOutboundMessages:

    def test_message(self, outbound_message):
        assert isinstance(outbound_message, OutboundMessage)
        assert str(outbound_message) == 'Sent message to test@example.com'

    def test_get_details(self, outbound_message):
        assert outbound_message.get().Body == 'Body example'

    def test_get_dump(self, outbound_message):
        assert outbound_message.get_dump() == 'Body example'

    def test_opens(self, outbound_message):
        with not_found():
            outbound_message.opens()


class TestInboundMessages:

    @pytest.fixture
    def inbound_message(self, postmark):
        return InboundMessage(postmark.messages.inbound, MessageID='123', Status='Blocked', From='test@example.com')

    def test_message(self, inbound_message):
        assert isinstance(inbound_message, InboundMessage)
        assert str(inbound_message) == 'Blocked message from test@example.com'

    def test_get_details(self, inbound_message):
        with not_found():
            inbound_message.get()

    def test_bypass(self, inbound_message):
        with not_found('[701] This message was not found or cannot be bypassed.'):
            inbound_message.bypass()

    def test_retry(self, inbound_message):
        with not_found('[701] This message was not found or cannot be retried.'):
            inbound_message.retry()

    def test_all(self, postmark):
        assert postmark.messages.inbound.all() == []

    def test_headers(self, inbound_webhook):
        assert inbound_webhook['X-Spam-Status'] == 'No'

    def test_not_existing_header(self, inbound_webhook):
        with pytest.raises(KeyError):
            assert inbound_webhook['Unknown']


class TestAttachment:

    def test_instance(self, attachment):
        assert isinstance(attachment, Attachment)

    def test_repr(self, attachment):
        assert repr(attachment) == '<Attachment: test.txt>'

    def test_len(self, attachment):
        assert len(attachment) == 45

    @pytest.mark.parametrize('attribute', ('ContentType', 'Name', 'ContentLength', 'Content'))
    def test_attributes(self, attachment, attribute):
        assert getattr(attachment, attribute) == attachment._data[attribute]

    def test_save(self, attachment, tmpdir):
        filename = tmpdir.join(attachment.Name)
        assert attachment.save(str(tmpdir)) == filename
        with filename.open() as fd:
            assert fd.read() == 'This is attachment contents, base-64 encoded.'

    def test_as_mime(self, attachment):
        message = attachment.as_mime()
        assert isinstance(message, MIMEBase)
        assert message['Content-Type'] == attachment.ContentType
        assert message['Content-Transfer-Encoding'] == 'base64'
        assert message['Content-Disposition'] == 'attachment; filename="test.txt"'
        assert message.get_payload(decode=True) == b'This is attachment contents, base-64 encoded.'


class TestOpens:

    def test_model(self, postmark):
        open = postmark.messages.outbound.opens.all(count=1)[0]
        assert isinstance(open, Open)
        assert str(open) == 'Open from test@example.com'

    def test_webhook(self, open_webhook):
        assert isinstance(open_webhook, Open)
        assert str(open_webhook) == 'Open from john@example.com'
