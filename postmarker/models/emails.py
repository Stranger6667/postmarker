# coding: utf-8
"""
This module provides basic ways to send emails.
"""
import mimetypes
import os
import sys
from base64 import b64encode
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..utils import chunks
from .base import Model, ModelManager


if sys.version_info[:2] <= (3, 2):
    SEPARATOR = ' '
else:
    SEPARATOR = ''


def list_to_csv(value):
    """
    Converts list to string with comma separated values. For string is no-op.
    """
    if isinstance(value, (list, tuple, set)):
        value = ','.join(value)
    return value


def guess_content_type(filename):
    content_type, encoding = mimetypes.guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    return content_type


def prepare_attachments(attachment):
    """
    Converts incoming attachment into dictionary.
    """
    if isinstance(attachment, tuple):
        result = {
            'Name': attachment[0],
            'Content': attachment[1],
            'ContentType': attachment[2],
        }
        if len(attachment) == 4:
            result['ContentID'] = attachment[3]
    elif isinstance(attachment, MIMEBase):
        result = {
            'Name': attachment.get_filename(),
            'Content': attachment.get_payload(),
            'ContentType': attachment.get_content_type(),
        }
        content_id = attachment.get('Content-ID')
        if content_id:
            if content_id.startswith('<') and content_id.endswith('>'):
                content_id = content_id[1:-1]
            if (attachment.get('Content-Disposition') or '').startswith('inline'):
                content_id = 'cid:%s' % content_id
            result['ContentID'] = content_id
    elif isinstance(attachment, str):
        content_type = guess_content_type(attachment)
        filename = os.path.basename(attachment)
        with open(attachment, 'rb') as fd:
            data = fd.read()
        result = {
            'Name': filename,
            'Content': b64encode(data).decode('utf-8'),
            'ContentType': content_type
        }
    else:
        result = attachment
    return result


def deconstruct_multipart(message):
    text, html, attachments = None, None, []
    for part in message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            text = part.get_payload(decode=True).decode('utf8')
        elif content_type == 'text/html':
            html = part.get_payload(decode=True).decode('utf8')
        elif content_type != 'multipart/alternative':
            attachments.append(part)
    return text, html, attachments


class BaseEmail(Model):

    def __init__(self, **kwargs):
        if not kwargs.get('Headers'):
            kwargs['Headers'] = {}
        if not kwargs.get('Attachments'):
            kwargs['Attachments'] = []
        super(BaseEmail, self).__init__(**kwargs)

    def __setitem__(self, key, value):
        self.Headers[key] = value

    def __delitem__(self, key):
        del self.Headers[key]

    def as_dict(self):
        """
        Additionally encodes headers.

        :return:
        """
        data = super(BaseEmail, self).as_dict()
        data['Headers'] = [{'Name': name, 'Value': value} for name, value in data['Headers'].items()]
        for field in ('To', 'Cc', 'Bcc'):
            if field in data:
                data[field] = list_to_csv(data[field])
        data['Attachments'] = [prepare_attachments(attachment) for attachment in data['Attachments']]
        return data

    def attach(self, *payloads):
        """
        Appends given payloads to the current payload.

        :param payloads:
        :type payloads: `dict`, `tuple`, `list`, `MIMEBase`
        :return: None.
        """
        self.Attachments.extend(payloads)

    def attach_binary(self, content, filename):
        """
        Attaches given binary data.

        :param bytes content: Binary data to be attached.
        :param str filename:
        :return: None.
        """
        content_type = guess_content_type(filename)
        payload = {
            'Name': filename,
            'Content': b64encode(content).decode('utf-8'),
            'ContentType': content_type
        }
        self.attach(payload)


def maybe_decode(value, encoding):
    if isinstance(value, bytes):
        if encoding is not None:
            value = value.decode(encoding)
        else:
            value = value.decode()
    return value


def prepare_header(value):
    if value is None:
        return value
    return SEPARATOR.join([maybe_decode(value, encoding) for value, encoding in decode_header(value)])


class Email(BaseEmail):

    def __init__(self, **kwargs):
        assert kwargs.get('TextBody') or kwargs.get('HtmlBody'), 'Provide either email TextBody or HtmlBody or both'
        super(Email, self).__init__(**kwargs)

    @classmethod
    def from_mime(cls, message, manager):
        """
        Instantiates ``Email`` instance from ``MIMEText`` instance.

        :param message: ``email.mime.text.MIMEText`` instance.
        :param manager: :py:class:`EmailManager` instance.
        :return: :py:class:`Email`
        """
        if isinstance(message, MIMEMultipart):
            text, html, attachments = deconstruct_multipart(message)
        else:
            text, html, attachments = message.get_payload(decode=True).decode('utf8'), None, []
        subject = prepare_header(message['Subject'])
        sender = prepare_header(message['From'])
        to = prepare_header(message['To'])
        cc = prepare_header(message['Cc'])
        bcc = prepare_header(message['Bcc'])
        reply_to = prepare_header(message['Reply-To'])
        tag = getattr(message, 'tag', None)
        return cls(manager=manager, From=sender, To=to, TextBody=text, HtmlBody=html, Subject=subject, Cc=cc, Bcc=bcc,
                   ReplyTo=reply_to, Attachments=attachments, Tag=tag)

    def send(self):
        return self._manager._send(**self.as_dict())


class EmailTemplate(BaseEmail):

    def send(self):
        return self._manager._send_with_template(**self.as_dict())


class EmailBatch(Model):
    """
    Gathers multiple emails in a single batch.
    """
    MAX_SIZE = 500

    def __init__(self, *emails, **kwargs):
        self.emails = emails
        super(EmailBatch, self).__init__(**kwargs)

    def __len__(self):
        return len(self.emails)

    def as_dict(self, **extra):
        """
        Converts all available emails to dictionaries.

        :return: List of dictionaries.
        """
        return [self._construct_email(email, **extra) for email in self.emails]

    def _construct_email(self, email, **extra):
        """
        Converts incoming data to properly structured dictionary.
        """
        if isinstance(email, dict):
            email = Email(manager=self._manager, **email)
        elif isinstance(email, (MIMEText, MIMEMultipart)):
            email = Email.from_mime(email, self._manager)
        elif not isinstance(email, Email):
            raise ValueError
        email._update(extra)
        return email.as_dict()

    def send(self, **extra):
        """
        Sends email batch.

        :return: Information about sent emails.
        :rtype: `list`
        """
        emails = self.as_dict(**extra)
        responses = [self._manager._send_batch(*batch) for batch in chunks(emails, self.MAX_SIZE)]
        return sum(responses, [])


class EmailManager(ModelManager):
    """
    Sends emails via Postmark REST API.
    """
    name = 'emails'

    def _send(self, **kwargs):
        """
        Low-level send call. Does not apply any transformation to given data.
        """
        return self.call('POST', '/email', data=kwargs)

    def _send_with_template(self, **kwargs):
        return self.call('POST', '/email/withTemplate/', data=kwargs)

    def _send_batch(self, *emails):
        """
        Low-level batch send call.
        """
        return self.call('POST', '/email/batch', data=emails)

    def send(self, message=None, From=None, To=None, Cc=None, Bcc=None, Subject=None, Tag=None, HtmlBody=None,
             TextBody=None, ReplyTo=None, Headers=None, TrackOpens=None, TrackLinks='None', Attachments=None):
        """
        Sends a single email.

        :param message: :py:class:`Email` or ``email.mime.text.MIMEText`` instance.
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
        assert (not (message and (From or To))), 'You should specify either message or From and To parameters'
        assert TrackLinks in ('None', 'HtmlAndText', 'HtmlOnly', 'TextOnly')
        if message is None:
            message = self.Email(From=From, To=To, Cc=Cc, Bcc=Bcc, Subject=Subject, Tag=Tag, HtmlBody=HtmlBody,
                                 TextBody=TextBody, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens,
                                 TrackLinks=TrackLinks, Attachments=Attachments)
        elif isinstance(message, (MIMEText, MIMEMultipart)):
            message = Email.from_mime(message, self)
        elif not isinstance(message, Email):
            raise TypeError('message should be either Email or MIMEText or MIMEMultipart instance')
        return message.send()

    def send_with_template(self, TemplateId, TemplateModel, From, To, Cc=None, Bcc=None, Subject=None, Tag=None,
                           ReplyTo=None, Headers=None, TrackOpens=None, TrackLinks='None', Attachments=None,
                           InlineCss=True):
        return self.EmailTemplate(TemplateId=TemplateId, TemplateModel=TemplateModel, From=From, To=To, Cc=Cc, Bcc=Bcc,
                                  Subject=Subject, Tag=Tag, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens,
                                  TrackLinks=TrackLinks, Attachments=Attachments, InlineCss=InlineCss).send()

    def send_batch(self, *emails, **extra):
        """
        Sends an email batch.

        :param emails: :py:class:`Email` instances or dictionaries
        :param extra: dictionary with extra arguments for every message in the batch.
        """
        return self.EmailBatch(*emails).send(**extra)

    # NOTE. The following methods are included here to expose better interface without need to import relevant classes.

    def Email(self, From, To, Cc=None, Bcc=None, Subject=None, Tag=None, HtmlBody=None, TextBody=None, ReplyTo=None,
              Headers=None, TrackOpens=None, TrackLinks='None', Attachments=None):
        """
        Constructs :py:class:`Email` instance.

        :return: :py:class:`Email`
        """
        return Email(manager=self, From=From, To=To, Cc=Cc, Bcc=Bcc, Subject=Subject, Tag=Tag, HtmlBody=HtmlBody,
                     TextBody=TextBody, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens, TrackLinks=TrackLinks,
                     Attachments=Attachments)

    def EmailTemplate(self, TemplateId, TemplateModel, From, To, Cc=None, Bcc=None, Subject=None, Tag=None,
                      ReplyTo=None, Headers=None, TrackOpens=None, TrackLinks='None', Attachments=None, InlineCss=True):
        """
        Constructs :py:class:`EmailTemplate` instance.

        :return: :py:class:`EmailTemplate`
        """
        return EmailTemplate(manager=self, TemplateId=TemplateId, TemplateModel=TemplateModel, From=From, To=To, Cc=Cc,
                             Bcc=Bcc, Subject=Subject, Tag=Tag, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens,
                             TrackLinks=TrackLinks, Attachments=Attachments, InlineCss=InlineCss)

    def EmailBatch(self, *emails):
        """
        Constructs :py:class:`EmailBatch` instance.

        :return: :py:class:`EmailBatch`
        """
        return EmailBatch(*emails, manager=self)
