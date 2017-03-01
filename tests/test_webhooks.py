# coding: utf-8
import json
from email.mime.base import MIMEBase

import pytest

from postmarker.webhooks import Attachment
from .conftest import INBOUND_WEBHOOK


def test_parsing(inbound_webhook):
    assert isinstance(inbound_webhook._data, dict)


def test_headers(inbound_webhook):
    assert inbound_webhook['X-Spam-Status'] == 'No'


def test_not_existing_header(inbound_webhook):
    with pytest.raises(KeyError):
        assert inbound_webhook['Unknown']


DECODED_HOOK = json.loads(INBOUND_WEBHOOK)
SIMPLE_ATTRIBUTES = [value for value in DECODED_HOOK.keys() if value != 'Attachments']


@pytest.mark.parametrize('attribute', SIMPLE_ATTRIBUTES)
def test_attribute(inbound_webhook, attribute):
    assert getattr(inbound_webhook, attribute) == inbound_webhook._data[attribute]


ATTACHMENT_ATTRIBUTES = DECODED_HOOK['Attachments'][0].keys()


class TestAttachment:

    def test_instance(self, attachment):
        assert isinstance(attachment, Attachment)

    def test_repr(self, attachment):
        assert repr(attachment) == '<Attachment: test.txt>'

    def test_len(self, attachment):
        assert len(attachment) == 45

    @pytest.mark.parametrize('attribute', ATTACHMENT_ATTRIBUTES)
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
