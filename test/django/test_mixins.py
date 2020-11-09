import pytest
from django.core.mail import EmailMultiAlternatives

from postmarker.django import PostmarkEmailMixin

pytestmark = pytest.mark.usefixtures("outbox")


class TaggedEmail(PostmarkEmailMixin, EmailMultiAlternatives):
    pass


def test_tags(postmark_request):
    TaggedEmail(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        tag="Test tag",
    ).send()
    assert postmark_request.call_args[1]["json"][0] == {
        "ReplyTo": None,
        "Subject": "Subject",
        "To": "receiver@example.com",
        "Bcc": None,
        "Headers": [],
        "Cc": None,
        "Attachments": [],
        "TextBody": "Body",
        "HtmlBody": None,
        "TrackOpens": True,
        "Tag": "Test tag",
        "Metadata": None,
        "MessageStream": None,
        "From": "sender@example.com",
    }


class EmailWithMetadata(PostmarkEmailMixin, EmailMultiAlternatives):
    pass


def test_metadata(postmark_request):
    EmailWithMetadata(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        metadata={"key1": "value1", "key2": "value2"},
    ).send()
    assert postmark_request.call_args[1]["json"][0] == {
        "ReplyTo": None,
        "Subject": "Subject",
        "To": "receiver@example.com",
        "Bcc": None,
        "Headers": [],
        "Cc": None,
        "Attachments": [],
        "TextBody": "Body",
        "HtmlBody": None,
        "TrackOpens": True,
        "Tag": None,
        "Metadata": {"key1": "value1", "key2": "value2"},
        "MessageStream": None,
        "From": "sender@example.com",
    }


class EmailWithMessageStream(PostmarkEmailMixin, EmailMultiAlternatives):
    pass


def test_metadata(postmark_request):
    EmailWithMessageStream(
        "Subject", "Body", "sender@example.com", ["receiver@example.com"], message_stream="example-message-stream"
    ).send()
    assert postmark_request.call_args[1]["json"][0] == {
        "ReplyTo": None,
        "Subject": "Subject",
        "To": "receiver@example.com",
        "Bcc": None,
        "Headers": [],
        "Cc": None,
        "Attachments": [],
        "TextBody": "Body",
        "HtmlBody": None,
        "TrackOpens": True,
        "Tag": None,
        "Metadata": None,
        "MessageStream": "example-message-stream",
        "From": "sender@example.com",
    }
