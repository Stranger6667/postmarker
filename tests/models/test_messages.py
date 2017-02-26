# coding: utf-8
from contextlib import contextmanager

import pytest

from postmarker.exceptions import ClientError
from postmarker.models.base import ModelManager
from postmarker.models.messages import InboundMessage, Open, OutboundMessage


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
        assert str(outbound_message) == "Sent message to test@example.com"

    def test_get_details(self, outbound_message):
        assert outbound_message.get_details()['Body'] == 'Body example'

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
            inbound_message.get_details()

    def test_bypass(self, inbound_message):
        with not_found('[701] This message was not found or cannot be bypassed.'):
            inbound_message.bypass()

    def test_retry(self, inbound_message):
        with not_found('[701] This message was not found or cannot be bypassed.'):
            inbound_message.retry()


def test_opens(postmark):
    open = postmark.messages.outbound.opens.all(count=1)[0]
    assert isinstance(open, Open)
    assert str(open) == 'Open from test@example.com'
