# coding: utf-8
import json
from email.mime.base import MIMEBase

import pytest

from postmarker.webhooks import Attachment, InboundWebhook

from .conftest import BOUNCE_WEBHOOK, DELIVERY_WEBHOOK, INBOUND_WEBHOOK, OPEN_WEBHOOK


DECODED_HOOK = json.loads(INBOUND_WEBHOOK)
SIMPLE_ATTRIBUTES = [value for value in DECODED_HOOK.keys() if value != 'Attachments']
ATTACHMENT_ATTRIBUTES = DECODED_HOOK['Attachments'][0].keys()


def test_parsing(inbound_webhook):
    assert inbound_webhook._data == DECODED_HOOK


def test_headers(inbound_webhook):
    assert inbound_webhook['X-Spam-Status'] == 'No'


def test_not_existing_header(inbound_webhook):
    with pytest.raises(KeyError):
        assert inbound_webhook['Unknown']


def test_init_with_parsed():
    instance = InboundWebhook(json=DECODED_HOOK)
    assert instance._data == DECODED_HOOK


def test_init_error():
    with pytest.raises(AssertionError) as exc:
        InboundWebhook(data=INBOUND_WEBHOOK, json=DECODED_HOOK)
    assert str(exc.value) == 'You could pass only `data` or `json`, not both'


@pytest.mark.parametrize('attribute', SIMPLE_ATTRIBUTES)
def test_attribute(inbound_webhook, attribute):
    assert getattr(inbound_webhook, attribute) == inbound_webhook._data[attribute]


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


DECODED_DELIVERY_HOOK = json.loads(DELIVERY_WEBHOOK)


@pytest.mark.parametrize('attribute', DECODED_DELIVERY_HOOK.keys())
def test_delivery_webhook(delivery_webhook, attribute):
    assert getattr(delivery_webhook, attribute) == delivery_webhook._data[attribute]


DECODED_OPEN_HOOK = json.loads(OPEN_WEBHOOK)


@pytest.mark.parametrize('attribute', DECODED_OPEN_HOOK.keys())
def test_open_webhook(open_webhook, attribute):
    assert getattr(open_webhook, attribute) == open_webhook._data[attribute]


DECODED_BOUNCE_HOOK = json.loads(BOUNCE_WEBHOOK)


@pytest.mark.parametrize('attribute', DECODED_BOUNCE_HOOK.keys())
def test_bounce_webhook(bounce_webhook, attribute):
    assert getattr(bounce_webhook, attribute) == bounce_webhook._data[attribute]
