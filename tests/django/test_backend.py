# coding: utf-8
from __future__ import unicode_literals

import sys
from contextlib import contextmanager

import pytest
from django import VERSION
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, send_mail, send_mass_mail
from requests import ConnectTimeout, Response

from postmarker.core import TEST_TOKEN
from postmarker.django import EmailBackend
from postmarker.django.signals import on_exception, post_send, pre_send
from postmarker.exceptions import PostmarkerException
from postmarker.models.emails import Email

from .._compat import patch


pytestmark = pytest.mark.usefixtures("outbox")


SEND_KWARGS = {
    "subject": "Subject here",
    "message": "Here is the message.",
    "from_email": "sender@example.com",
    "recipient_list": ["receiver@example.com"],
}


def send_with_connection(connection):
    mail.EmailMessage("Subject", "Body", "sender@example.com", ["receiver@example.com"], connection=connection).send()


def test_send_mail(postmark_request, settings):
    send_mail(**SEND_KWARGS)
    assert postmark_request.call_args[1]["json"] == (
        {
            "ReplyTo": None,
            "Subject": "Subject here",
            "To": "receiver@example.com",
            "Bcc": None,
            "Headers": [],
            "Cc": None,
            "Attachments": [],
            "TextBody": "Here is the message.",
            "HtmlBody": None,
            "Tag": None,
            "Metadata": None,
            "TrackOpens": False,
            "From": "sender@example.com",
        },
    )
    assert postmark_request.call_args[1]["headers"]["X-Postmark-Server-Token"] == settings.POSTMARK["TOKEN"]


@pytest.mark.parametrize(
    "kwarg, key",
    (
        ("bcc", "Bcc"),
        ("cc", "Cc"),
        pytest.mark.skipif(VERSION[:2] < (1, 7), reason="Django < 1.7 doesn't support `reply_to`")(
            ("reply_to", "ReplyTo")
        ),
    ),
)
def test_reply_to_cc_bcc(postmark_request, kwarg, key):
    message = mail.EmailMessage(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        **{kwarg: ["r1@example.com", "r2@example.com"]}
    )
    message.send()
    assert postmark_request.call_args[1]["json"][0][key] == "r1@example.com, r2@example.com"


EXAMPLE_BATCH_RESPONSE = [
    {
        "ErrorCode": 0,
        "Message": "OK",
        "MessageID": "b7bc2f4a-e38e-4336-af7d-e6c392c2f817",
        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
        "To": "receiver@example.com",
    },
    {
        "ErrorCode": 406,
        "Message": "Bla bla, inactive recipient",
        "MessageID": "e2ecbbfc-fe12-463d-b933-9fe22915106d",
        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
        "To": "invalid@example.com",
    },
]


class TestMassSend:
    messages = [
        ("Subject", "Body", "sender@example.com", ["receiver@example.com"]),
        ("Subject", "Body", "sender@example.com", ["invalid@example.com"]),
    ]

    @pytest.fixture
    def batch_send(self):
        @contextmanager
        def manager(return_value=EXAMPLE_BATCH_RESPONSE):
            with patch("postmarker.models.emails.EmailBatch.send", return_value=return_value) as send:
                yield send

        return manager

    def test_send_mass(self, batch_send):
        with batch_send() as send:
            assert send_mass_mail([]) is None
            assert not send.called

    def test_sent_messages_count(self, batch_send):
        with batch_send():
            assert send_mass_mail(self.messages, fail_silently=True) == 1

    def test_single_exception_propagation(self, batch_send):
        with batch_send():
            with pytest.raises(PostmarkerException) as exc:
                send_mass_mail(self.messages, fail_silently=False)
            assert str(exc.value) == "[406] Bla bla, inactive recipient"

    def test_multiple_exceptions_propagation(self, batch_send):
        with batch_send(EXAMPLE_BATCH_RESPONSE * 2):
            with pytest.raises(PostmarkerException) as exc:
                send_mass_mail(self.messages * 2, fail_silently=False)
            assert str(exc.value) == "[[406] Bla bla, inactive recipient, [406] Bla bla, inactive recipient]"


@pytest.fixture
def message():
    return EmailMultiAlternatives(
        subject="subject", body="text_content", from_email="sender@example.com", to=["receiver@example.com"]
    )


def test_send_mail_with_attachment(postmark_request, message):
    """
    Test sending email with attachment

    The Django backend crashes when sending an email with an attachment.
    https://github.com/Stranger6667/postmarker/issues/98

    This test does not send any mail. Instead, it demonstrates the bug by
    constructing the same underlying datastructures that the backend would
    construct.
    """
    message.attach("hello.txt", "Hello World", "text/plain")
    message.send()
    assert postmark_request.call_args[1]["json"][0] == {
        "TextBody": "text_content",
        "Attachments": [{"Name": "hello.txt", "Content": "Hello World", "ContentType": "text/plain"}],
        "From": "sender@example.com",
        "HtmlBody": None,
        "ReplyTo": None,
        "Subject": "subject",
        "To": "receiver@example.com",
        "Headers": [],
        "TrackOpens": False,
        "Cc": None,
        "Bcc": None,
        "Tag": None,
        "Metadata": None,
    }


def test_text_html_alternative_and_pdf_attachment_failure(postmark_request, message):
    """
    Send a text body, HTML alternative, and PDF attachment.
    """
    message.attach_alternative("<html></html>", "text/html")
    if sys.version_info[:2] == (3, 2):
        content = b"PDF-File-Contents"
    else:
        content = "PDF-File-Contents"
    message.attach("hello.pdf", content, "application/pdf")
    message.send(fail_silently=False)
    if sys.version_info[0] < 3:
        encoded_content = "UERGLUZpbGUtQ29udGVudHM="
    else:
        encoded_content = "UERGLUZpbGUtQ29udGVudHM=\n"
    assert postmark_request.call_args[1]["json"][0] == {
        "Attachments": [{"Content": encoded_content, "ContentType": "application/pdf", "Name": "hello.pdf"}],
        "Bcc": None,
        "Cc": None,
        "From": "sender@example.com",
        "Headers": [],
        "HtmlBody": "<html></html>",
        "ReplyTo": None,
        "Subject": "subject",
        "Tag": None,
        "Metadata": None,
        "TextBody": "text_content",
        "To": "receiver@example.com",
        "TrackOpens": False,
    }


def test_message_rfc822(postmark_request, message):
    if sys.version_info[:2] == (3, 2):
        message_content = b"Fake message"
        expected_content = "RmFrZSBtZXNzYWdl\n"
    else:
        message_content = "Fake message"
        expected_content = "RmFrZSBtZXNzYWdl"
    message.attach_alternative(message_content, "message/rfc822")
    message.send(fail_silently=False)
    assert postmark_request.call_args[1]["json"][0] == {
        "Attachments": [{"Name": "attachment.txt", "Content": expected_content, "ContentType": "message/rfc822"}],
        "Bcc": None,
        "Cc": None,
        "From": "sender@example.com",
        "Headers": [],
        "HtmlBody": None,
        "ReplyTo": None,
        "Subject": "subject",
        "Tag": None,
        "Metadata": None,
        "TextBody": "text_content",
        "To": "receiver@example.com",
        "TrackOpens": False,
    }


def test_headers_encoding(postmark_request):
    kwargs = {
        "subject": "Тест",
        "message": "Here is the message.",
        "from_email": "Тест <sender@example.com>",
        "recipient_list": ["Тест <receiver@example.com>", "Тест2 <receiver@example.com>"],
    }
    send_mail(**kwargs)
    request = postmark_request.call_args[1]["json"][0]
    assert request["Subject"] == kwargs["subject"]
    assert request["From"] == kwargs["from_email"]
    assert request["To"] == ", ".join(kwargs["recipient_list"])


@pytest.mark.skipif(
    VERSION[:2] < (1, 7), reason="Django < 1.7 does not support `html_message` argument in `send_mail` function."
)
@pytest.mark.parametrize(
    "html_message",
    (
        "<html></html>",
        "<html>Тест</html>",
        """<html>
       <body>
           <div>
             %s
           </div>
       </body>
       </html>"""
        % ("." * 1000),
    ),
)
def test_send_mail_html_message(html_message, postmark_request):
    send_mail(html_message=html_message, **SEND_KWARGS)
    assert postmark_request.call_args[1]["json"] == (
        {
            "ReplyTo": None,
            "Subject": "Subject here",
            "To": "receiver@example.com",
            "Bcc": None,
            "Headers": [],
            "Cc": None,
            "Attachments": [],
            "TextBody": "Here is the message.",
            "HtmlBody": html_message,
            "TrackOpens": False,
            "Tag": None,
            "Metadata": None,
            "From": "sender@example.com",
        },
    )


def test_send_long_text_line(postmark_request):
    kwargs = SEND_KWARGS.copy()
    message = "A" * 1000
    kwargs["message"] = message
    send_mail(**kwargs)
    assert postmark_request.call_args[1]["json"] == (
        {
            "ReplyTo": None,
            "Subject": "Subject here",
            "To": "receiver@example.com",
            "Bcc": None,
            "Headers": [],
            "Cc": None,
            "Attachments": [],
            "TextBody": message,
            "HtmlBody": None,
            "TrackOpens": False,
            "Tag": None,
            "Metadata": None,
            "From": "sender@example.com",
        },
    )


def test_missing_api_key(settings):
    settings.POSTMARK = {}
    with pytest.raises(ImproperlyConfigured) as exc:
        send_mail(**SEND_KWARGS)
    assert str(exc.value) == "You should specify TOKEN to use Postmark email backend"


def test_test_mode(settings, postmark_request):
    settings.POSTMARK = {"TEST_MODE": True}
    send_mail(**SEND_KWARGS)
    assert postmark_request.call_args[1]["headers"]["X-Postmark-Server-Token"] == TEST_TOKEN


def test_extra_options(settings, postmark_request):
    settings.POSTMARK["TRACK_OPENS"] = True
    send_mail(**SEND_KWARGS)
    assert postmark_request.call_args[1]["json"] == (
        {
            "ReplyTo": None,
            "Subject": "Subject here",
            "To": "receiver@example.com",
            "Bcc": None,
            "Headers": [],
            "Cc": None,
            "Attachments": [],
            "TextBody": "Here is the message.",
            "HtmlBody": None,
            "Tag": None,
            "Metadata": None,
            "TrackOpens": True,
            "From": "sender@example.com",
        },
    )


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason="Context manager protocol was added in Django 1.8")
def test_context_manager(postmark_request):
    with mail.get_connection() as connection:
        send_with_connection(connection)
    assert postmark_request.call_args[1]["json"] == (
        {
            "ReplyTo": None,
            "Subject": "Subject",
            "To": "receiver@example.com",
            "Bcc": None,
            "Headers": [],
            "Cc": None,
            "Attachments": [],
            "TextBody": "Body",
            "HtmlBody": None,
            "Tag": None,
            "Metadata": None,
            "TrackOpens": True,
            "From": "sender@example.com",
        },
    )


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason="Context manager protocol was added in Django 1.8")
class TestExceptions:
    @pytest.fixture(autouse=True)
    def setup(self, postmark_request):
        postmark_request.return_value.json.side_effect = ValueError

    def test_silent_exception(self):
        with mail.get_connection(fail_silently=True) as connection:
            send_with_connection(connection)

    def test_loud_exception(self):
        with mail.get_connection() as connection:
            with pytest.raises(ValueError):
                send_with_connection(connection)


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason="Context manager protocol was added in Django 1.8")
def test_close_closed_connection():
    with mail.get_connection() as connection:
        connection.close()


@pytest.mark.usefixtures("postmark_request")
class TestSignals:
    def test_pre_send(self, catch_signal):
        with catch_signal(pre_send) as handler:
            send_mail(**SEND_KWARGS)
        assert handler.called
        kwargs = handler.call_args[1]
        assert kwargs["sender"] == EmailBackend
        assert kwargs["signal"] == pre_send
        assert len(kwargs["messages"]) == 1
        message = kwargs["messages"][0]
        assert Email.from_mime(message, None).as_dict() == {
            "Attachments": [],
            "Bcc": None,
            "Cc": None,
            "From": "sender@example.com",
            "Headers": [],
            "HtmlBody": None,
            "ReplyTo": None,
            "Subject": "Subject here",
            "Tag": None,
            "Metadata": None,
            "TextBody": "Here is the message.",
            "To": "receiver@example.com",
        }

    def test_post_send(self, catch_signal, postmark_request):
        postmark_request.return_value = Response()
        postmark_request.return_value.status_code = 200
        postmark_request.return_value._content = (
            b'[{"ErrorCode": 0, "To": "receiver@example.com", '
            b'"SubmittedAt": "2016-10-06T10:05:30.570118-04:00", '
            b'"Message": "Test job accepted", '
            b'"MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686"}]'
        )
        with catch_signal(post_send) as handler:
            send_mail(**SEND_KWARGS)
        assert handler.called
        kwargs = handler.call_args[1]
        assert kwargs["sender"] == EmailBackend
        assert kwargs["signal"] == post_send
        assert kwargs["response"] == [
            {
                "ErrorCode": 0,
                "Message": "Test job accepted",
                "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686",
                "SubmittedAt": "2016-10-06T10:05:30.570118-04:00",
                "To": "receiver@example.com",
            }
        ]

    def test_on_exception(self, catch_signal):
        with patch("requests.Session.request", side_effect=ConnectTimeout):
            with catch_signal(on_exception) as handler:
                send_mail(fail_silently=True, **SEND_KWARGS)
        assert handler.called
        kwargs = handler.call_args[1]
        assert kwargs["sender"] == EmailBackend
        assert kwargs["signal"] == on_exception
        assert isinstance(kwargs["exception"], ConnectTimeout)
        assert len(kwargs["raw_messages"]) == 1
