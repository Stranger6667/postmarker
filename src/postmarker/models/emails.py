"""Basic ways to send emails."""

from __future__ import annotations

import mimetypes
import os
from base64 import b64encode
from email.header import decode_header
from email.message import Message, MIMEPart
from typing import Any, cast

from ..utils import chunks
from .base import MessageModel, Model, ModelManager

SEPARATOR = ""

# What `list_to_csv` joins
Recipients = str | list[str] | tuple[str, ...] | set[str]
# What `prepare_attachments` accepts
AttachmentData = dict[str, Any] | tuple[str, ...] | Message | str


def list_to_csv(value: Recipients | None) -> str | None:
    """Converts list to string with comma separated values. For string is no-op."""
    if isinstance(value, (list, tuple, set)):
        return ",".join(value)
    return value


def guess_content_type(filename: str) -> str:
    content_type, encoding = mimetypes.guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    return content_type


def prepare_attachments(attachment: AttachmentData) -> dict[str, Any]:
    """Converts incoming attachment into dictionary."""
    result: dict[str, Any]
    if isinstance(attachment, tuple):
        result = {
            "Name": attachment[0],
            "Content": attachment[1],
            "ContentType": attachment[2],
        }
        if len(attachment) == 4:
            result["ContentID"] = attachment[3]
    elif isinstance(attachment, Message):
        payload: Any = attachment.get_payload()
        content_type = attachment.get_content_type()
        # Postmark requires base64 content for every attachment, including `message/rfc822`.
        # A payload without `Content-Transfer-Encoding` is expected to be base64 already
        if content_type == "message/rfc822" and not isinstance(payload, str):
            payload = b64encode(payload[0].get_payload(decode=True)).decode()
        elif "Content-Transfer-Encoding" in attachment:
            payload = b64encode(cast(bytes, attachment.get_payload(decode=True))).decode()
        result = {
            "Name": attachment.get_filename() or "attachment.txt",
            "Content": payload,
            "ContentType": content_type,
        }
        content_id = attachment.get("Content-ID")
        if content_id:
            if content_id.startswith("<") and content_id.endswith(">"):
                content_id = content_id[1:-1]
            if (attachment.get("Content-Disposition") or "").startswith("inline"):
                content_id = f"cid:{content_id}"
            result["ContentID"] = content_id
    elif isinstance(attachment, str):
        content_type = guess_content_type(attachment)
        filename = os.path.basename(attachment)
        with open(attachment, "rb") as fd:
            data = fd.read()
        result = {
            "Name": filename,
            "Content": b64encode(data).decode("utf-8"),
            "ContentType": content_type,
        }
    else:
        result = attachment
    return result


def get_body(part: Message) -> str:
    payload = cast(bytes, part.get_payload(decode=True))
    body = payload.decode("utf8")
    # `set_content` (the modern email API, used by Django 6+) always appends a newline
    if isinstance(part, MIMEPart):
        body = body.removesuffix("\n")
    return body


def deconstruct_multipart_recursive(
    seen: set[Message], text: list[str], html: list[str], attachments: list[Message], message: Message
) -> None:
    if message in seen:
        return
    seen.add(message)
    if message.get_content_maintype() == "multipart":
        for part in message.walk():
            deconstruct_multipart_recursive(seen, text, html, attachments, part)
    else:
        content_type = message.get_content_type()
        if content_type == "text/plain" and not text:
            text.append(get_body(message))
        elif content_type == "text/html" and not html:
            html.append(get_body(message))
        else:
            # Ignore underlying messages inside `message/rfc822` payload, because the message itself will be passed
            # as an attachment
            if content_type == "message/rfc822":
                for part in cast(list[Message], message.get_payload()):
                    seen.add(part)
            attachments.append(message)


def deconstruct_multipart(message: Message) -> tuple[str | None, str | None, list[Message]]:
    seen: set[Message] = set()
    text: list[str] = []
    html: list[str] = []
    attachments: list[Message] = []
    deconstruct_multipart_recursive(seen, text, html, attachments, message)
    return (text and text[0]) or None, (html and html[0]) or None, attachments


class BaseEmail(Model):
    def __init__(self, **kwargs: Any) -> None:
        if not kwargs.get("Headers"):
            kwargs["Headers"] = {}
        if not kwargs.get("Attachments"):
            kwargs["Attachments"] = []
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return "{} from {} to {}".format(
            self.__class__.__name__, self._data.get("From"), list_to_csv(self._data.get("To"))
        )

    def __setitem__(self, key: str, value: str) -> None:
        self.Headers[key] = value

    def __delitem__(self, key: str) -> None:
        del self.Headers[key]

    def as_dict(self) -> dict[str, Any]:
        """Additionally encodes headers.

        :return:
        """
        data = super().as_dict()
        data["Headers"] = [{"Name": name, "Value": value} for name, value in data["Headers"].items()]
        for field in ("To", "Cc", "Bcc"):
            if field in data:
                data[field] = list_to_csv(data[field])
        data["Attachments"] = [prepare_attachments(attachment) for attachment in data["Attachments"]]
        return data

    def attach(self, *payloads: AttachmentData) -> None:
        """Appends given payloads to the current payload.

        :param payloads:
        :type payloads: `dict`, `tuple`, `list`, `email.message.Message`
        :return: None.
        """
        self.Attachments.extend(payloads)

    def attach_binary(self, content: bytes, filename: str) -> None:
        """Attaches given binary data.

        :param bytes content: Binary data to be attached.
        :param str filename:
        :return: None.
        """
        content_type = guess_content_type(filename)
        payload = {
            "Name": filename,
            "Content": b64encode(content).decode("utf-8"),
            "ContentType": content_type,
        }
        self.attach(payload)


def maybe_decode(value: str | bytes, encoding: str | None) -> str:
    if isinstance(value, bytes):
        if encoding is not None:
            value = value.decode(encoding)
        else:
            value = value.decode()
    return value


def prepare_header(value: Any) -> str | None:
    if value is None:
        return value
    return SEPARATOR.join([maybe_decode(value, encoding) for value, encoding in decode_header(value)])


class Email(BaseEmail):
    def __init__(self, **kwargs: Any) -> None:
        assert kwargs.get("TextBody") or kwargs.get("HtmlBody"), "Provide either email TextBody or HtmlBody or both"
        super().__init__(**kwargs)

    @classmethod
    def from_mime(cls, message: Message, manager: Any) -> Email:
        """Instantiates ``Email`` instance from ``email.message.Message`` instance.

        :param message: ``email.message.Message`` instance.
        :param manager: :py:class:`EmailManager` instance.
        :return: :py:class:`Email`
        """
        text, html, attachments = deconstruct_multipart(message)
        subject = prepare_header(message["Subject"])
        sender = prepare_header(message["From"])
        to = prepare_header(message["To"])
        cc = prepare_header(message["Cc"])
        bcc = prepare_header(message["Bcc"])
        reply_to = prepare_header(message["Reply-To"])
        tag = getattr(message, "tag", None)
        metadata = getattr(message, "metadata", None)
        message_stream = getattr(message, "message_stream", None)
        return cls(
            manager=manager,
            From=sender,
            To=to,
            TextBody=text,
            HtmlBody=html,
            Subject=subject,
            Cc=cc,
            Bcc=bcc,
            ReplyTo=reply_to,
            Attachments=attachments,
            Tag=tag,
            Metadata=metadata,
            MessageStream=message_stream,
        )

    def send(self) -> Any:
        return self._manager._send(**self.as_dict())


class EmailTemplate(BaseEmail):
    def __init__(self, **kwargs: Any) -> None:
        if kwargs.get("TemplateId") is None and kwargs.get("TemplateAlias") is None:
            raise ValueError("You need to specify either TemplateId or TemplateAlias")
        super().__init__(**kwargs)

    def send(self) -> Any:
        return self._manager._send_with_template(**self.as_dict())


class EmailTemplateBatch(Model):
    """Gathers multiple email templates in a single batch."""

    MAX_SIZE = 500

    def __init__(self, *emails: EmailTemplate | dict[str, Any], **kwargs: Any) -> None:
        self.emails = emails
        super().__init__(**kwargs)

    def __len__(self) -> int:
        return len(self.emails)

    # Batches serialize to a list of emails
    def as_dict(self, **extra: Any) -> list[dict[str, Any]]:  # type: ignore[override]
        """Converts all available emails to dictionaries.

        :return: List of dictionaries.
        """
        return [self._construct_email(email, **extra) for email in self.emails]

    def _construct_email(self, email: EmailTemplate | dict[str, Any], **extra: Any) -> dict[str, Any]:
        """Converts incoming data to properly structured dictionary."""
        if isinstance(email, dict):
            email = EmailTemplate(manager=self._manager, **email)
        elif not isinstance(email, EmailTemplate):
            raise ValueError
        email._update(extra)
        return email.as_dict()

    def send(self, **extra: Any) -> list[Any]:
        """Sends email batch.

        :return: Information about sent emails.
        :rtype: `list`
        """
        emails = self.as_dict(**extra)
        responses = [self._manager._send_batch_with_template(*batch) for batch in chunks(emails, self.MAX_SIZE)]
        return sum(responses, [])


class EmailBatch(Model):
    """Gathers multiple emails in a single batch."""

    MAX_SIZE = 500

    def __init__(self, *emails: Email | Message | dict[str, Any], **kwargs: Any) -> None:
        self.emails = emails
        super().__init__(**kwargs)

    def __len__(self) -> int:
        return len(self.emails)

    # Batches serialize to a list of emails
    def as_dict(self, **extra: Any) -> list[dict[str, Any]]:  # type: ignore[override]
        """Converts all available emails to dictionaries.

        :return: List of dictionaries.
        """
        return [self._construct_email(email, **extra) for email in self.emails]

    def _construct_email(self, email: Email | Message | dict[str, Any], **extra: Any) -> dict[str, Any]:
        """Converts incoming data to properly structured dictionary."""
        if isinstance(email, dict):
            email = Email(manager=self._manager, **email)
        elif isinstance(email, Message):
            email = Email.from_mime(email, self._manager)
        elif not isinstance(email, Email):
            raise ValueError
        email._update(extra)
        return email.as_dict()

    def send(self, **extra: Any) -> list[Any]:
        """Sends email batch.

        :return: Information about sent emails.
        :rtype: `list`
        """
        emails = self.as_dict(**extra)
        responses = [self._manager._send_batch(*batch) for batch in chunks(emails, self.MAX_SIZE)]
        return sum(responses, [])


class Delivery(MessageModel):
    def __str__(self) -> str:
        return "Delivery to {}".format(self._data.get("Recipient"))


# The `EmailManager` methods of the same name shadow these classes in its body
_Email = Email
_EmailTemplate = EmailTemplate


class EmailManager(ModelManager[Model]):
    """Sends emails via Postmark REST API."""

    name = "emails"

    def _send(self, **kwargs: Any) -> Any:
        """Low-level send call. Does not apply any transformation to given data."""
        return self.call("POST", "/email", data=kwargs)

    def _send_with_template(self, **kwargs: Any) -> Any:
        return self.call("POST", "/email/withTemplate/", data=kwargs)

    def _send_batch_with_template(self, *email_templates: dict[str, Any]) -> Any:
        return self.call("POST", "/email/batchWithTemplates/", data={"Messages": email_templates})

    def _send_batch(self, *emails: dict[str, Any]) -> Any:
        """Low-level batch send call."""
        return self.call("POST", "/email/batch", data=emails)

    def send(
        self,
        message: Email | Message | None = None,
        From: str | None = None,
        To: Recipients | None = None,
        Cc: Recipients | None = None,
        Bcc: Recipients | None = None,
        Subject: str | None = None,
        Tag: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Metadata: dict[str, Any] | None = None,
        ReplyTo: str | None = None,
        Headers: dict[str, str] | None = None,
        TrackOpens: bool | None = None,
        TrackLinks: str = "None",
        Attachments: list[AttachmentData] | None = None,
        MessageStream: str | None = None,
    ) -> Any:
        """Sends a single email.

        :param message: :py:class:`Email` or ``email.message.Message`` instance.
        :param str From: The sender email address.
        :param To: Recipient's email address.
                   Multiple recipients could be specified as a list or string with comma separated values.
        :type To: str or list
        :param Cc: Cc recipient's email address.
                   Multiple Cc recipients could be specified as a list or string with comma separated values.
        :type Cc: str or list
        :param Bcc: Bcc recipient's email address.
                    Multiple Bcc recipients could be specified as a list or string with comma separated values.
        :type Bcc: str or list
        :param str Subject: Email subject.
        :param str Tag: Email tag.
        :param str HtmlBody: HTML email message.
        :param str TextBody: Plain text email message.
        :param str ReplyTo: Reply To override email address.
        :param dict Headers: Dictionary of custom headers to include.
        :param bool TrackOpens: Activate open tracking for this email.
        :param str TrackLinks: Activate link tracking for links in the HTML or Text bodies of this email.
        :param list Attachments: List of attachments.
        :return: Information about sent email.
        :rtype: `dict`
        """
        assert not (message and (From or To)), "You should specify either message or From and To parameters"
        assert TrackLinks in ("None", "HtmlAndText", "HtmlOnly", "TextOnly")
        email: Email
        if message is None:
            email = self.Email(
                From=From,
                To=To,
                Cc=Cc,
                Bcc=Bcc,
                Subject=Subject,
                Tag=Tag,
                HtmlBody=HtmlBody,
                TextBody=TextBody,
                Metadata=Metadata,
                ReplyTo=ReplyTo,
                Headers=Headers,
                TrackOpens=TrackOpens,
                TrackLinks=TrackLinks,
                Attachments=Attachments,
                MessageStream=MessageStream,
            )
        elif isinstance(message, Message):
            email = Email.from_mime(message, self)
        elif isinstance(message, Email):
            email = message
        else:
            # Runtime guard for callers without type checking
            raise TypeError("message should be either Email or email.message.Message instance")
        return email.send()

    def send_with_template(
        self,
        *,
        TemplateId: int | None = None,
        TemplateModel: dict[str, Any],
        From: str,
        To: Recipients,
        TemplateAlias: str | None = None,
        Cc: Recipients | None = None,
        Bcc: Recipients | None = None,
        Subject: str | None = None,
        Tag: str | None = None,
        ReplyTo: str | None = None,
        Headers: dict[str, str] | None = None,
        TrackOpens: bool | None = None,
        TrackLinks: str = "None",
        Attachments: list[AttachmentData] | None = None,
        InlineCss: bool = True,
        Metadata: dict[str, Any] | None = None,
        MessageStream: str | None = None,
    ) -> Any:
        return self.EmailTemplate(
            TemplateId=TemplateId,
            TemplateAlias=TemplateAlias,
            TemplateModel=TemplateModel,
            From=From,
            To=To,
            Cc=Cc,
            Bcc=Bcc,
            Subject=Subject,
            Tag=Tag,
            ReplyTo=ReplyTo,
            Headers=Headers,
            TrackOpens=TrackOpens,
            TrackLinks=TrackLinks,
            Attachments=Attachments,
            InlineCss=InlineCss,
            Metadata=Metadata,
            MessageStream=MessageStream,
        ).send()

    def send_batch(self, *emails: Email | Message | dict[str, Any], **extra: Any) -> list[Any]:
        """Sends an email batch.

        :param emails: :py:class:`Email` instances or dictionaries
        :param extra: dictionary with extra arguments for every message in the batch.
        """
        return self.EmailBatch(*emails).send(**extra)

    def send_template_batch(self, *emails: EmailTemplate | dict[str, Any], **extra: Any) -> list[Any]:
        """Sends an email batch.

        :param emails: :py:class:`EmailTemplate` instances or dictionaries
        :param extra: dictionary with extra arguments for every message in the batch.
        """
        return self.EmailTemplateBatch(*emails).send(**extra)

    # NOTE. The following methods are included here to expose better interface without need to import relevant classes.

    def Email(
        self,
        From: str | None,
        To: Recipients | None,
        Cc: Recipients | None = None,
        Bcc: Recipients | None = None,
        Subject: str | None = None,
        Tag: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Metadata: dict[str, Any] | None = None,
        ReplyTo: str | None = None,
        Headers: dict[str, str] | None = None,
        TrackOpens: bool | None = None,
        TrackLinks: str = "None",
        Attachments: list[AttachmentData] | None = None,
        MessageStream: str | None = None,
    ) -> Email:
        """Constructs :py:class:`Email` instance.

        :return: :py:class:`Email`
        """
        return Email(
            manager=self,
            From=From,
            To=To,
            Cc=Cc,
            Bcc=Bcc,
            Subject=Subject,
            Tag=Tag,
            HtmlBody=HtmlBody,
            TextBody=TextBody,
            Metadata=Metadata,
            ReplyTo=ReplyTo,
            Headers=Headers,
            TrackOpens=TrackOpens,
            TrackLinks=TrackLinks,
            Attachments=Attachments,
            MessageStream=MessageStream,
        )

    def EmailTemplate(
        self,
        *,
        TemplateId: int | None = None,
        TemplateModel: dict[str, Any],
        From: str,
        To: Recipients,
        TemplateAlias: str | None = None,
        Cc: Recipients | None = None,
        Bcc: Recipients | None = None,
        Subject: str | None = None,
        Tag: str | None = None,
        ReplyTo: str | None = None,
        Headers: dict[str, str] | None = None,
        TrackOpens: bool | None = None,
        TrackLinks: str = "None",
        Attachments: list[AttachmentData] | None = None,
        InlineCss: bool = True,
        Metadata: dict[str, Any] | None = None,
        MessageStream: str | None = None,
    ) -> EmailTemplate:
        """Constructs :py:class:`EmailTemplate` instance.

        :return: :py:class:`EmailTemplate`
        """
        return EmailTemplate(
            manager=self,
            TemplateId=TemplateId,
            TemplateAlias=TemplateAlias,
            TemplateModel=TemplateModel,
            From=From,
            To=To,
            Cc=Cc,
            Bcc=Bcc,
            Subject=Subject,
            Tag=Tag,
            ReplyTo=ReplyTo,
            Headers=Headers,
            TrackOpens=TrackOpens,
            TrackLinks=TrackLinks,
            Attachments=Attachments,
            InlineCss=InlineCss,
            Metadata=Metadata,
            MessageStream=MessageStream,
        )

    def EmailBatch(self, *emails: _Email | Message | dict[str, Any]) -> EmailBatch:
        """Constructs :py:class:`EmailBatch` instance.

        :return: :py:class:`EmailBatch`
        """
        return EmailBatch(*emails, manager=self)

    def EmailTemplateBatch(self, *emails: _EmailTemplate | dict[str, Any]) -> EmailTemplateBatch:
        """Constructs :py:class:`EmailTemplateBatch` instance.

        :return: :py:class:`EmailTemplateBatch`
        """
        return EmailTemplateBatch(*emails, manager=self)
