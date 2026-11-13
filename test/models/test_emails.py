import base64
import os
import platform
import re
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import css_inline
import pytest

from postmarker.core import PostmarkClient
from postmarker.models.emails import Email

pytestmark = pytest.mark.vcr


def get_attachment_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), f"attachments/{filename}"))


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
ENCODED_CONTENT = "dGVzdCBjb250ZW50"

IMAGE = MIMEImage(b"test content", "png", name="image1.png")
IMAGE.add_header("Content-ID", "<image1@example.com>")
IMAGE_NO_BRACKETS = MIMEImage(b"test content", "png", name="image2.png")
IMAGE_NO_BRACKETS.add_header("Content-ID", "image2@example.com")
INLINE_IMAGE = MIMEImage(b"test content", "png", name="image3.png")
INLINE_IMAGE.add_header("Content-ID", "<image3@example.com>")
INLINE_IMAGE.add_header("Content-Disposition", "inline", filename="image3.png")


@pytest.fixture
def minimal_data():
    return {
        "From": "sender@example.com",
        "To": "receiver@example.com",
        "Subject": "Postmark test",
        "HtmlBody": "<html><body><strong>Hello</strong> dear Postmark user.</body></html>",
    }


def test_simple_send_default(postmark, minimal_data):
    """Minimal case."""
    response = postmark.emails.send(**minimal_data)
    assert response == {
        "ErrorCode": 0,
        "Message": "Test job accepted",
        "MessageID": "806aa9ad-689d-48d3-9887-ac0c2bc6f57d",
        "SubmittedAt": "2016-10-06T04:24:31.2196962-04:00",
        "To": "receiver@example.com",
    }


def test_simple_send_mime_text(postmark):
    response = postmark.emails.send(message=MIME_MESSAGE)
    assert response == {
        "ErrorCode": 0,
        "Message": "Test job accepted",
        "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686",
        "SubmittedAt": "2016-10-06T10:05:30.570118-04:00",
        "To": "receiver@example.com",
    }


def test_simple_send_minimum_mime(postmark):
    message = get_mime_message("Text", From="sender@example.com", To="receiver@example.com")
    response = postmark.emails.send(message=message)
    assert response == {
        "ErrorCode": 0,
        "Message": "Test job accepted",
        "MessageID": "03285bf8-2a7d-4c42-9e15-b51062e2bc9a",
        "SubmittedAt": "2016-10-06T10:26:27.8804172-04:00",
        "To": "receiver@example.com",
    }


def test_simple_send_invalid(postmark):
    with pytest.raises(TypeError) as exc:
        postmark.emails.send(message=object())
    assert str(exc.value) == "message should be either Email or email.message.Message instance"


def test_simple_send_message_and_kwargs(postmark, email):
    with pytest.raises(AssertionError) as exc:
        postmark.emails.send(message=email, From="test@test.com")
    assert str(exc.value).startswith("You should specify either message or From and To parameters")


def test_simple_send_email(postmark, email, postmark_request):
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
def test_simple_send_multiple_addresses(postmark, minimal_data, postmark_request, field, value):
    minimal_data[field] = value
    postmark.emails.send(**minimal_data)
    assert postmark_request.call_args[1]["json"][field] == "first@example.com,second@example.com"


def test_simple_send_headers(postmark, minimal_data, postmark_request):
    minimal_data["Headers"] = {"Test": 1}
    postmark.emails.send(**minimal_data)
    assert postmark_request.call_args[1]["json"]["Headers"] == [{"Name": "Test", "Value": 1}]


def test_simple_send_message_stream(postmark, minimal_data, postmark_request):
    minimal_data["MessageStream"] = "example-message-stream"
    postmark.emails.send(**minimal_data)
    assert postmark_request.call_args[1]["json"]["MessageStream"] == "example-message-stream"


@pytest.mark.parametrize("attachment", SUPPORTED_ATTACHMENTS)
def test_simple_send_attachments(postmark, minimal_data, postmark_request, attachment):
    minimal_data["Attachments"] = [attachment]
    postmark.emails.send(**minimal_data)
    assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]


def test_simple_send_mime_multipart(postmark, postmark_request):
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


def test_simple_send_with_template(postmark):
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


def test_simple_send_template_with_alias_only(postmark):
    # It should be possible to specify `TemplateAlias` and not `TemplateId`
    postmark.emails.EmailTemplate(
        TemplateAlias="foo",
        TemplateModel={},
        From="sender@example.com",
        To="receiver@example.com",
    )


def test_simple_send_with_template_without_alias_and_id(postmark):
    # If there is no `TemplateAlias` and `TemplateId` then it is an error
    with pytest.raises(ValueError):
        postmark.emails.send_with_template(
            TemplateModel={},
            From="sender@example.com",
            To="receiver@example.com",
        )


def test_batch_send_email_instance(postmark, email, postmark_request):
    postmark.emails.send_batch(email)
    assert postmark_request.call_args[1]["json"] == (email.as_dict(),)


def test_batch_send_dict(postmark, email, postmark_request):
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


def test_batch_send_multiple(postmark, email, postmark_request):
    postmark.emails.send_batch(email, email)
    assert postmark_request.call_args[1]["json"] == (
        email.as_dict(),
        email.as_dict(),
    )


def test_batch_send_mime(postmark, postmark_request):
    postmark.emails.send_batch(MIME_MESSAGE)
    email = Email.from_mime(MIME_MESSAGE, postmark.emails)
    assert postmark_request.call_args[1]["json"] == (email.as_dict(),)


def test_batch_send_invalid(postmark):
    expected = "Expected Email, email.message.Message or dict, got object"
    with pytest.raises(ValueError, match=f"^{re.escape(expected)}$"):
        postmark.emails.send_batch(object())


@pytest.mark.parametrize("container", [list, tuple])
def test_batch_send_sequence(postmark, email, container):
    expected = (
        f"Expected Email, email.message.Message or dict, got {container.__name__}; "
        "pass emails as separate arguments, e.g. send_batch(*emails)"
    )
    with pytest.raises(ValueError, match=f"^{re.escape(expected)}$"):
        postmark.emails.send_batch(container([email, email]))


def test_email_batch_len(email_batch):
    assert len(email_batch) == 1


def test_email_str(email):
    assert str(email) == "Email from sender@example.com to receiver@example.com"


def test_email_repr(email):
    assert repr(email) == "<Email from sender@example.com to receiver@example.com>"


def test_email_str_multiple_recipients(postmark):
    email = postmark.emails.Email(From="sender@example.com", To=["a@example.com", "b@example.com"], TextBody="text")
    assert str(email) == "Email from sender@example.com to a@example.com,b@example.com"


def test_email_set_header(email):
    assert email.Headers == {}
    email["X-Accept-Language"] = "en-us, en"
    assert email.Headers == {"X-Accept-Language": "en-us, en"}
    assert email.as_dict()["Headers"] == [{"Name": "X-Accept-Language", "Value": "en-us, en"}]


def test_email_unset_header(email):
    email["X-Accept-Language"] = "en-us, en"
    del email["X-Accept-Language"]
    assert email.Headers == {}
    assert email.as_dict()["Headers"] == []


def test_email_body():
    with pytest.raises(AssertionError) as exc:
        Email(
            From="sender@example.com",
            To="receiver@example.com",
            Subject="Postmark test",
        )
    assert str(exc.value).startswith("Provide either email TextBody or HtmlBody or both")


@pytest.mark.parametrize("attachment", SUPPORTED_ATTACHMENTS)
def test_email_attach(email, postmark_request, attachment):
    email.attach(attachment)
    email.send()
    assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]


def test_email_attach_multiple(email, postmark_request):
    email.attach(ATTACHMENT, TUPLE_ATTACHMENT, MIME_ATTACHMENT)
    email.send()
    assert postmark_request.call_args[1]["json"]["Attachments"] == [
        ATTACHMENT,
        ATTACHMENT,
        ATTACHMENT,
    ]


def test_email_attach_unknown_content_type(email, postmark_request):
    email.attach(UNKNOWN_TYPE_ATTACHMENT)
    email.send()
    assert postmark_request.call_args[1]["json"]["Attachments"] == [
        {
            "Name": "report.blabla",
            "Content": CONTENT,
            "ContentType": "application/octet-stream",
        }
    ]


def test_email_attach_binary(email, postmark_request):
    email.attach_binary(RAW_CONTENT, "readme.txt")
    email.send()
    assert postmark_request.call_args[1]["json"]["Attachments"] == [ATTACHMENT]


def test_email_from_mime(postmark):
    email = Email.from_mime(MIME_MESSAGE, postmark.emails)
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
def test_email_inline_image(email, postmark_request, image, expected):
    email.attach(image)
    email.send()
    assert postmark_request.call_args[1]["json"]["Attachments"] == [expected]


def test_delivery_str(delivery_webhook):
    assert str(delivery_webhook) == "Delivery to john@example.com"


def test_template_batch_send_email_template(postmark, email_template, postmark_request):
    postmark.emails.send_template_batch(email_template)
    assert postmark_request.call_args[1]["json"] == {"Messages": (email_template.as_dict(),)}


def test_template_batch_send_dict(postmark, postmark_request):
    template_dict = {
        "TemplateId": 983381,
        "TemplateModel": {},
        "From": "sender@example.com",
        "To": "receiver@example.com",
    }
    expected = {
        "TemplateId": 983381,
        "TemplateModel": {},
        "From": "sender@example.com",
        "To": "receiver@example.com",
        "Headers": [],
        "Attachments": [],
    }
    postmark.emails.send_template_batch(template_dict)
    assert postmark_request.call_args[1]["json"] == {"Messages": (expected,)}


def test_template_batch_send_multiple(postmark, email_template, postmark_request):
    postmark.emails.send_template_batch(email_template, email_template)
    assert postmark_request.call_args[1]["json"] == {
        "Messages": (
            email_template.as_dict(),
            email_template.as_dict(),
        )
    }


def test_template_batch_send_invalid(postmark):
    expected = "Expected EmailTemplate or dict, got object"
    with pytest.raises(ValueError, match=f"^{re.escape(expected)}$"):
        postmark.emails.send_template_batch(object())


@pytest.mark.parametrize("container", [list, tuple])
def test_template_batch_send_sequence(postmark, email_template, container):
    expected = (
        f"Expected EmailTemplate or dict, got {container.__name__}; "
        "pass emails as separate arguments, e.g. send_template_batch(*emails)"
    )
    with pytest.raises(ValueError, match=f"^{re.escape(expected)}$"):
        postmark.emails.send_template_batch(container([email_template, email_template]))


def test_email_template_str(email_template):
    assert str(email_template) == "EmailTemplate from sender@example.com to receiver@example.com"


def test_email_template_repr(email_template):
    assert repr(email_template) == "<EmailTemplate from sender@example.com to receiver@example.com>"


def test_email_template_batch_len(email_template_batch):
    assert len(email_template_batch) == 1


STYLED_HTML = "<html><head><style>h1{color:red}</style></head><body><h1>Hi</h1></body></html>"
INLINED_HTML = '<html><head></head><body><h1 style="color: red;">Hi</h1></body></html>'
STYLED_EMAIL = {"From": "sender@example.com", "To": "receiver@example.com", "HtmlBody": STYLED_HTML}


def sent_html_body(postmark_request):
    payload = postmark_request.call_args[1]["json"]
    # Batches send a tuple of emails
    if isinstance(payload, tuple):
        payload = payload[0]
    return payload["HtmlBody"]


@pytest.mark.parametrize(
    "send",
    (
        lambda client: client.emails.send(**STYLED_EMAIL),
        lambda client: client.emails.send(message=get_mime_message("Text", STYLED_HTML, **DEFAULT_HEADERS)),
        lambda client: client.emails.send_batch(STYLED_EMAIL),
        lambda client: client.emails.send_batch(get_mime_message("Text", STYLED_HTML, **DEFAULT_HEADERS)),
    ),
    ids=("send", "send-mime", "batch", "batch-mime"),
)
def test_inline_css(postmark_request, send):
    send(PostmarkClient(server_token="SERVER_TOKEN", inline_css=True))
    assert sent_html_body(postmark_request) == INLINED_HTML


def test_inline_css_from_config(postmark_request):
    client = PostmarkClient.from_config({"postmark_server_token": "SERVER_TOKEN", "postmark_inline_css": True})
    client.emails.send(**STYLED_EMAIL)
    assert sent_html_body(postmark_request) == INLINED_HTML


def test_inline_css_custom_inliner(postmark_request):
    client = PostmarkClient(server_token="SERVER_TOKEN", inline_css=css_inline.CSSInliner(keep_style_tags=True))
    client.emails.send(**STYLED_EMAIL)
    assert (
        sent_html_body(postmark_request)
        == '<html><head><style>h1{color:red}</style></head><body><h1 style="color: red;">Hi</h1></body></html>'
    )


def test_inline_css_skips_remote_stylesheets(postmark_request):
    # Email HTML may carry user content; the default inliner must not fetch `<link>` URLs
    html = '<html><head><link rel="stylesheet" href="http://127.0.0.1:9/x.css"></head><body>Hi</body></html>'
    PostmarkClient(server_token="SERVER_TOKEN", inline_css=True).emails.send(**{**STYLED_EMAIL, "HtmlBody": html})
    assert sent_html_body(postmark_request) == "<html><head></head><body>Hi</body></html>"


def test_inline_css_missing_package(monkeypatch):
    monkeypatch.setitem(sys.modules, "css_inline", None)
    with pytest.raises(ImportError, match=r"postmarker\[css-inline\]"):
        PostmarkClient(server_token="SERVER_TOKEN", inline_css=True)
