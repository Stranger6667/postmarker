from base64 import b64decode
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import join

from .base import MessageModel, Model, ModelManager, SubModelManager


class Open(MessageModel):
    def __str__(self):
        return "Open from %s" % self._data.get("Recipient")


class OpensManager(ModelManager):
    name = "opens"
    model = Open

    def all(
        self,
        count=500,
        offset=0,
        recipient=None,
        tag=None,
        client_name=None,
        client_company=None,
        client_family=None,
        os_name=None,
        os_family=None,
        os_company=None,
        platform=None,
        country=None,
        region=None,
        city=None,
    ):
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

    def get(self, id, count=500, offset=0):
        return self.call("GET", "/messages/outbound/opens/%s" % id, count=count, offset=offset)

    def Open(self, json):
        return self.model.from_json(json, manager=self)


class BaseMessage(Model):
    def get(self):
        return self._manager.get(self.MessageID)


class OutboundMessage(BaseMessage):
    def __str__(self):
        recipients = ", ".join(self._data.get("Recipients"))
        return "{} message to {}".format(self._data.get("Status"), recipients)

    def get_dump(self):
        return self._manager.get_dump(self.MessageID)

    def opens(self, count=500, offset=0):
        return self._manager.opens.get(self.MessageID, count=count, offset=offset)


class OutboundMessageManager(SubModelManager):
    name = "outbound"
    model = OutboundMessage
    _managers = (OpensManager,)

    def all(
        self,
        count=500,
        offset=0,
        recipient=None,
        fromemail=None,
        tag=None,
        status=None,
        todate=None,
        fromdate=None,
        subject=None,
    ):
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

    def get(self, id):
        response = self.call("GET", "/messages/outbound/%s/details" % id)
        return self._init_instance(response)

    def get_dump(self, id):
        return self.call("GET", "/messages/outbound/%s/dump" % id).get("Body")


class InboundMessage(BaseMessage):
    def __str__(self):
        return "{} message from {}".format(self._data.get("Status"), self._data.get("From"))

    def __getitem__(self, item):
        for header in self._data["Headers"]:
            if header["Name"] == item:
                return header["Value"]
        raise KeyError

    @property
    def Attachments(self):
        attachments = self._data.get("Attachments", ())
        return [Attachment(**data) for data in attachments]

    def bypass(self):
        return self._manager.bypass(self.MessageID)

    def retry(self):
        return self._manager.retry(self.MessageID)

    def as_mime(self):
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
    def __str__(self):
        return self.Name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"

    def __len__(self):
        return self.ContentLength

    @property
    def decoded(self):
        return b64decode(self.Content.encode("ascii"))

    def save(self, directory):
        filename = join(directory, self.Name)
        with open(filename, "wb") as fd:
            fd.write(self.decoded)
        return filename

    def as_mime(self):
        maintype, subtype = self.ContentType.split("/")
        message = MIMEBase(maintype, subtype)
        message.set_payload(self.Content)
        message["Content-Transfer-Encoding"] = "base64"
        message.add_header("Content-Disposition", "attachment", filename=self.Name)
        return message


class InboundMessageManager(ModelManager):
    name = "inbound"
    model = InboundMessage

    def all(
        self,
        count=500,
        offset=0,
        recipient=None,
        fromemail=None,
        tag=None,
        subject=None,
        mailboxhash=None,
        status=None,
        todate=None,
        fromdate=None,
    ):
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

    def get(self, id):
        response = self.call("GET", "/messages/inbound/%s/details" % id)
        return self._init_instance(response)

    def bypass(self, id):
        return self.call("PUT", "/messages/inbound/%s/bypass" % id)

    def retry(self, id):
        return self.call("PUT", "/messages/inbound/%s/retry" % id)

    def InboundMessage(self, json):
        return self.model.from_json(json, manager=self)


class MessageManager(SubModelManager):
    name = "messages"
    _managers = (OutboundMessageManager, InboundMessageManager)
