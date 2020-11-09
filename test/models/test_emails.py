import base64
import os
import platform
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest

from postmarker.models.emails import Email

CASSETTE_NAME = "emails"


def get_attachment_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "attachments/%s" % filename))


if platform.system() in {"Linux", "Darwin"}:
    RAW_CONTENT = b"test content\n"
else:
    RAW_CONTENT = b"test content\r\n"
CONTENT = base64.b64encode(RAW_CONTENT).decode()


ATTACHMENT = {
    "Name": "readme.txt",
    "Content": CONTENT,
    "ContentType": "text/plain",
}
TUPLE_ATTACHMENT = ATTACHMENT["Name"], ATTACHMENT["Content"], ATTACHMENT["ContentType"]
MIME_ATTACHMENT = MIMEBase("text", "plain")
MIME_ATTACHMENT.set_payload(CONTENT)
MIME_ATTACHMENT.add_header("Content-Disposition", "attachment", filename="readme.txt")
PATH_ATTACHMENT = get_attachment_path("readme.txt")

SUPPORTED_ATTACHMENTS = (ATTACHMENT, MIME_ATTACHMENT, TUPLE_ATTACHMENT, PATH_ATTACHMENT)

UNKNOWN_TYPE_ATTACHMENT = get_attachment_path("report.blabla")


DEFAULT_HEADERS = {
    "From": "sender@example.com",
    "To": "receiver@example.com",
    "Subject": "Test subject",
    "Cc": "cc@example.com",
    "Bcc": "bcc@example.com",
    "Reply-To": "replyto@example.com",
}


def get_mime_message(text, html_text=None, **kwargs):
    if not html_text:
        instance = MIMEText(text)
    else:
        instance = MIMEMultipart("alternative")
        instance.attach(MIMEText(text, "plain"))
        instance.attach(MIMEText(html_text, "html"))
        extra = MIMEBase("application", "octet-stream")
        extra.set_payload(b"test content")
        encoders.encode_base64(extra)
        extra.add_header("Content-Disposition", "attachment", filename="report.pdf")
        instance.attach(extra)
        instance["X-Accept-Language"] = "en-us, en"
    for key, value in kwargs.items():
        instance[key] = value
    return instance


MIME_MESSAGE = get_mime_message("Text", **DEFAULT_HEADERS)
MIME_ALTERNATIVE = get_mime_message("Text", "HTML content", **DEFAULT_HEADERS)
ENCODED_CONTENT = "dGVzdCBjb250ZW50\n"

IMAGE = MIMEImage(b"test content", "png", name="image1.png")
IMAGE.add_header("Content-ID", "<image1@example.com>")
IMAGE_NO_BRACKETS = MIMEImage(b"test content", "png", name="image2.png")
IMAGE_NO_BRACKETS.add_header("Content-ID", "image2@example.com")
INLINE_IMAGE = MIMEImage(b"test content", "png", name="image3.png")
INLINE_IMAGE.add_header("Content-ID", "<image3@example.com>")
INLINE_IMAGE.add_header("Content-Disposition", "inline", filename="image3.png")


class TestSimpleSend:
    @pytest.fixture
    def minimal_data(self):
        return {
            "From": "sender@example.com",
            "To": "receiver@example.com",
            "Subject": "Postmark test",
            "HtmlBody": "<html><body><strong>Hello</strong> dear Postmark user.</body></html>",
        }

    def test_default(self, postmark, minimal_data):
        """Minimal case."""
        response = postmark.emails.send(**minimal_data)
        assert response == {
            "ErrorCode": 0,
            "Message": "Test job accepted",
            "MessageID": "806aa9ad-689d-48d3-9887-ac0c2bc6f57d",
            "SubmittedAt": "2016-10-06T04:24:31.2196962-04:00",
            "To": "receiver@example.com",
        }

    def test_mime_text(self, postmark):
        response = postmark.emails.send(message=MIME_MESSAGE)
        assert response == {
            "ErrorCode": 0,
            "Message": "Test job accepted",
            "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686",
            "SubmittedAt": "2016-10-06T10:05:30.570118-04:00",
            "To": "receiver@example.com",
        }

    def test_minimum_mime(self, postmark):
        message = get_mime_message("Text", From="sender@example.com", To="receiver@example.com")
        response = postmark.emails.send(message=message)
        assert response == {
            "ErrorCode": 0,
            "Message": "Test job accepted",
            "MessageID": "03285bf8-2a7d-4c42-9e15-b51062e2bc9a",
            "SubmittedAt": "2016-10-06T10:26:27.8804172-04:00",
            "To": "receiver@example.com",
        }

    def test_invalid(self, postmark):
        with pytest.raises(TypeError) as exc:
            postmark.emails.send(message=object())
        assert str(exc.value) == "message should be either Email or MIMEText or MIMEMultipart instance"

    def test_message_and_kwargs(self, postmark, email):
        with pytest.raises(AssertionError) as exc:
            postmark.emails.send(message=email, From="test@test.com")
        assert str(exc.value).startswith("You should specify either message or From and To parameters")

    def test_send_email(self, postmark, email, postmark_request):
        postmark.emails.send(message=email)
        assert postmark_request.call_args[1]["json"] == email.as_dict()

    @pytest.mark.parametrize("field", ("To", "Cc", "Bcc"))
    @pytest.mark.parametrize(
        "value",
        (
            "first@example.com,second@example.com",
            ["first@example.com", "second@example.com"],
        ),
    )
    def test_multiple_addresses(self, postmark, minimal_data, postmark_request, field, value):
        minimal_data[field] = value
        postmark.emails.send(**minimal_data)
        assert postmark_request.call_args[1]["json"][field] == "first@example.com,second@example.com"

    def test_headers(self, postmark, minimal_data, postmark_request):
        minimal_data["Headers"] = {"Test": 1}
        postmark.emails.send(**minimal_data)
        assert postmark_request.call_args[1]["json"]["Headers"] == [{"Name": "Test", "Value": 1}]

    def test_message_stream(self, postmark, minimal_data, postmark_request):
        minimal_data["MessageStream"] = "example-message-stream"
        postmark.emails.send(**minimal_data)
        assert postmark_request.call_args[1]["json"]["MessageStream"] == "example-message-stream"

    @pytest.mark.parametrize("attachment", SUPPORTED_ATTACHMENTS)
    def test_attachments(self, postmark, minimal_data, postmark_request, attachment):
        minimal_data["Attachments"] = [attachment]
        postmark.emails.send(**minimal_data)
        assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]

    def test_mime_multipart(self, postmark, postmark_request):
        postmark.emails.send(MIME_ALTERNATIVE)
        assert postmark_request.call_args[1]["json"] == {
            "Attachments": [
                {
                    "Content": ENCODED_CONTENT,
                    "ContentType": "application/octet-stream",
                    "Name": "report.pdf",
                }
            ],
            "Bcc": "bcc@example.com",
            "Cc": "cc@example.com",
            "From": "sender@example.com",
            "Headers": [],
            "HtmlBody": "HTML content",
            "ReplyTo": "replyto@example.com",
            "Subject": "Test subject",
            "TextBody": "Text",
            "Tag": None,
            "Metadata": None,
            "MessageStream": None,
            "To": "receiver@example.com",
        }

    def test_send_with_template(self, postmark):
        response = postmark.emails.send_with_template(
            TemplateId=983381,
            TemplateModel={},
            From="sender@example.com",
            To="receiver@example.com",
        )
        assert response == {
            "ErrorCode": 0,
            "Message": "OK",
            "MessageID": "cf639975-1685-4c70-aba1-b1115b4f6d12",
            "SubmittedAt": "2016-10-15T14:42:56.1508279-04:00",
            "To": "receiver@example.com",
        }


class TestBatchSend:
    def test_email_instance(self, postmark, email, postmark_request):
        postmark.emails.send_batch(email)
        assert postmark_request.call_args[1]["json"] == (email.as_dict(),)

    def test_dict(self, postmark, email, postmark_request):
        email_dict = {"From": email.From, "To": email.To, "TextBody": email.TextBody}
        expected = {
            "From": email.From,
            "To": email.To,
            "TextBody": email.TextBody,
            "Headers": [],
            "Attachments": [],
        }
        postmark.emails.send_batch(email_dict)
        assert postmark_request.call_args[1]["json"] == (expected,)

    def test_multiple(self, postmark, email, postmark_request):
        postmark.emails.send_batch(email, email)
        assert postmark_request.call_args[1]["json"] == (
            email.as_dict(),
            email.as_dict(),
        )

    def test_mime(self, postmark, postmark_request):
        postmark.emails.send_batch(MIME_MESSAGE)
        email = Email.from_mime(MIME_MESSAGE, postmark)
        assert postmark_request.call_args[1]["json"] == (email.as_dict(),)

    def test_invalid(self, postmark):
        with pytest.raises(ValueError):
            postmark.emails.send_batch(object())


class TestEmailBatch:
    def test_len(self, email_batch):
        assert len(email_batch) == 1


class TestEmail:
    def test_set_header(self, email):
        assert email.Headers == {}
        email["X-Accept-Language"] = "en-us, en"
        assert email.Headers == {"X-Accept-Language": "en-us, en"}
        assert email.as_dict()["Headers"] == [{"Name": "X-Accept-Language", "Value": "en-us, en"}]

    def test_unset_header(self, email):
        email["X-Accept-Language"] = "en-us, en"
        del email["X-Accept-Language"]
        assert email.Headers == {}
        assert email.as_dict()["Headers"] == []

    def test_body(self):
        with pytest.raises(AssertionError) as exc:
            Email(
                From="sender@example.com",
                To="receiver@example.com",
                Subject="Postmark test",
            )
        assert str(exc.value).startswith("Provide either email TextBody or HtmlBody or both")

    @pytest.mark.parametrize("attachment", SUPPORTED_ATTACHMENTS)
    def test_attach(self, email, postmark_request, attachment):
        email.attach(attachment)
        email.send()
        assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]

    def test_attach_multiple(self, email, postmark_request):
        email.attach(ATTACHMENT, TUPLE_ATTACHMENT, MIME_ATTACHMENT)
        email.send()
        assert postmark_request.call_args[1]["json"]["Attachments"] == [
            ATTACHMENT,
            ATTACHMENT,
            ATTACHMENT,
        ]

    def test_attach_unknown_content_type(self, email, postmark_request):
        email.attach(UNKNOWN_TYPE_ATTACHMENT)
        email.send()
        assert postmark_request.call_args[1]["json"]["Attachments"] == [
            {
                "Name": "report.blabla",
                "Content": CONTENT,
                "ContentType": "application/octet-stream",
            }
        ]

    def test_attach_binary(self, email, postmark_request):
        email.attach_binary(RAW_CONTENT, "readme.txt")
        email.send()
        assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]

    def test_from_mime(self, postmark):
        email = Email.from_mime(MIME_MESSAGE, postmark)
        assert email.TextBody == "Text"
        assert email.From == MIME_MESSAGE["From"]
        assert email.To == MIME_MESSAGE["To"]
        assert email.Subject == MIME_MESSAGE["Subject"]
        assert email.Cc == MIME_MESSAGE["Cc"]
        assert email.Bcc == MIME_MESSAGE["Bcc"]
        assert email.ReplyTo == MIME_MESSAGE["Reply-To"]

    @pytest.mark.parametrize(
        "image, expected",
        (
            (
                ("image", "content", "image/png", "cid:image@example.com"),
                {
                    "Name": "image",
                    "Content": "content",
                    "ContentType": "image/png",
                    "ContentID": "cid:image@example.com",
                },
            ),
            (
                IMAGE,
                {
                    "Name": "image1.png",
                    "Content": ENCODED_CONTENT,
                    "ContentType": "image/png",
                    "ContentID": "image1@example.com",
                },
            ),
            (
                IMAGE_NO_BRACKETS,
                {
                    "Name": "image2.png",
                    "Content": ENCODED_CONTENT,
                    "ContentType": "image/png",
                    "ContentID": "image2@example.com",
                },
            ),
            (
                INLINE_IMAGE,
                {
                    "Name": "image3.png",
                    "Content": ENCODED_CONTENT,
                    "ContentType": "image/png",
                    "ContentID": "cid:image3@example.com",
                },
            ),
        ),
    )
    def test_inline_image(self, email, postmark_request, image, expected):
        email.attach(image)
        email.send()
        assert postmark_request.call_args[1]["json"]["Attachments"] == [expected]


class TestDelivery:
    def test_str(self, delivery_webhook):
        assert str(delivery_webhook) == "Delivery to john@example.com"
