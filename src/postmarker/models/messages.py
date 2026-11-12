from __future__ import annotations

from base64 import b64decode
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import join
from typing import Any

from .base import MessageModel, Model, ModelManager, SubModelManager


class Open(MessageModel):
    def __str__(self) -> str:
        return "Open from {}".format(self._data.get("Recipient"))


class OpensManager(ModelManager[Open]):
    name = "opens"
    model = Open
    pagination_limit = 10000

    def all(
        self,
        count: int | None = 500,
        offset: int = 0,
        recipient: str | None = None,
        tag: str | None = None,
        client_name: str | None = None,
        client_company: str | None = None,
        client_family: str | None = None,
        os_name: str | None = None,
        os_family: str | None = None,
        os_company: str | None = None,
        platform: str | None = None,
        country: str | None = None,
        region: str | None = None,
        city: str | None = None,
    ) -> list[Open]:
        responses = self.call_many(
            "GET",
            "/messages/outbound/opens",
            count=count,
            offset=offset,
            recipient=recipient,
            tag=tag,
            client_name=client_name,
            client_company=client_company,
            client_family=client_family,
            os_name=os_name,
            os_family=os_family,
            os_company=os_company,
            platform=platform,
            country=country,
            region=region,
            city=city,
        )
        return self.expand_responses(responses, "Opens")

    def get(self, id: str, count: int = 500, offset: int = 0) -> Any:
        return self.call("GET", f"/messages/outbound/opens/{id}", count=count, offset=offset)

    def Open(self, json: str | bytes) -> Open:
        return self.model.from_json(json, manager=self)


class BaseMessage(Model):
    def get(self) -> Any:
        return self._manager.get(self.MessageID)


class OutboundMessage(BaseMessage):
    def __str__(self) -> str:
        recipients = ", ".join(self._data["Recipients"])
        return "{} message to {}".format(self._data.get("Status"), recipients)

    def get_dump(self) -> Any:
        return self._manager.get_dump(self.MessageID)

    def opens(self, count: int = 500, offset: int = 0) -> Any:
        return self._manager.opens.get(self.MessageID, count=count, offset=offset)


class OutboundMessageManager(SubModelManager[OutboundMessage]):
    name = "outbound"
    opens: OpensManager
    model = OutboundMessage
    pagination_limit = 10000
    _managers = (OpensManager,)

    def all(
        self,
        count: int | None = 500,
        offset: int = 0,
        recipient: str | None = None,
        fromemail: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        todate: Any = None,
        fromdate: Any = None,
        subject: str | None = None,
    ) -> list[OutboundMessage]:
        """All outbound messages.

        Lets you get all the details about any outbound or inbound message that you sent or received
        through a specific server. Messages expire after 45 days.

        :param int count: Number of messages to return per request.
        :param int offset: Number of messages to skip.
        :param str recipient: Filter by the user who was receiving the email.
        :param str fromemail: Filter by the sender email address.
        :param str tag: Filter by tag.
        :param str status: Filter by status (queued or sent).
        :param date todate: Filter messages up to the date specified (inclusive).
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :param subject: Filter by email subject.
        :return: A list of :py:class:`OutboundMessage` instances.
        :rtype: `list`
        """
        responses = self.call_many(
            "GET",
            "/messages/outbound",
            count=count,
            offset=offset,
            recipient=recipient,
            fromemail=fromemail,
            tag=tag,
            status=status,
            todate=todate,
            fromdate=fromdate,
            subject=subject,
        )
        return self.expand_responses(responses, "Messages")

    def get(self, id: str) -> OutboundMessage:
        response = self.call("GET", f"/messages/outbound/{id}/details")
        return self._init_instance(response)

    def get_dump(self, id: str) -> Any:
        return self.call("GET", f"/messages/outbound/{id}/dump").get("Body")


class InboundMessage(BaseMessage):
    def __str__(self) -> str:
        return "{} message from {}".format(self._data.get("Status"), self._data.get("From"))

    def __getitem__(self, item: str) -> Any:
        for header in self._data["Headers"]:
            if header["Name"] == item:
                return header["Value"]
        raise KeyError

    @property
    def Attachments(self) -> list[Attachment]:
        attachments = self._data.get("Attachments", ())
        return [Attachment(**data) for data in attachments]

    def bypass(self) -> Any:
        return self._manager.bypass(self.MessageID)

    def retry(self) -> Any:
        return self._manager.retry(self.MessageID)

    def as_mime(self) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(self.TextBody, "plain"))
        message.attach(MIMEText(self.HtmlBody, "html"))
        for header in self._data["Headers"]:
            message.add_header(header["Name"], header["Value"])

        for key in ("Subject", "From", "To", "Date", "MessageID", "Cc", "Bcc"):
            value = getattr(self, key, None)
            if value:
                message[key] = value
        message["Reply-To"] = self.ReplyTo
        for attachment in self.Attachments:
            message.attach(attachment.as_mime())
        return message


class Attachment(Model):
    def __str__(self) -> str:
        return str(self.Name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"

    def __len__(self) -> int:
        return int(self.ContentLength)

    @property
    def decoded(self) -> bytes:
        return b64decode(self.Content.encode("ascii"))

    def save(self, directory: str) -> str:
        filename = join(directory, self.Name)
        with open(filename, "wb") as fd:
            fd.write(self.decoded)
        return filename

    def as_mime(self) -> MIMEBase:
        maintype, subtype = self.ContentType.split("/")
        message = MIMEBase(maintype, subtype)
        message.set_payload(self.Content)
        message["Content-Transfer-Encoding"] = "base64"
        message.add_header("Content-Disposition", "attachment", filename=self.Name)
        return message


class InboundMessageManager(ModelManager[InboundMessage]):
    name = "inbound"
    model = InboundMessage
    pagination_limit = 10000

    def all(
        self,
        count: int | None = 500,
        offset: int = 0,
        recipient: str | None = None,
        fromemail: str | None = None,
        tag: str | None = None,
        subject: str | None = None,
        mailboxhash: str | None = None,
        status: str | None = None,
        todate: Any = None,
        fromdate: Any = None,
    ) -> list[InboundMessage]:
        """All inbound messages.

        :param count: Number of messages to return per request.
        :param offset: Number of messages to skip.
        :param recipient: Filter by the user who was receiving the email.
        :param fromemail: Filter by the sender email address.
        :param tag: Filter by tag.
        :param subject: Filter by email subject.
        :param mailboxhash: Filter by mailboxhash.
        :param status: Filter by status (blocked, processed, queued, failed, scheduled).
        :param date todate: Filter messages up to the date specified (inclusive).
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :return: A list of :py:class:`InboundMessage` instances.
        :rtype: `list`
        """
        responses = self.call_many(
            "GET",
            "/messages/inbound",
            count=count,
            offset=offset,
            recipient=recipient,
            fromemail=fromemail,
            tag=tag,
            subject=subject,
            mailboxhash=mailboxhash,
            status=status,
            todate=todate,
            fromdate=fromdate,
        )
        return self.expand_responses(responses, "InboundMessages")

    def get(self, id: str) -> InboundMessage:
        response = self.call("GET", f"/messages/inbound/{id}/details")
        return self._init_instance(response)

    def bypass(self, id: str) -> Any:
        return self.call("PUT", f"/messages/inbound/{id}/bypass")

    def retry(self, id: str) -> Any:
        return self.call("PUT", f"/messages/inbound/{id}/retry")

    def InboundMessage(self, json: str | bytes) -> InboundMessage:
        return self.model.from_json(json, manager=self)


class MessageManager(SubModelManager[Model]):
    name = "messages"
    outbound: OutboundMessageManager
    inbound: InboundMessageManager
    _managers = (OutboundMessageManager, InboundMessageManager)
