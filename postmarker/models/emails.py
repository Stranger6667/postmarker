# coding: utf-8
"""
This module provides basic ways to send emails.
"""
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from .base import Model, ModelManager


def list_to_csv(value):
    """
    Converts list to string with comma separated values. For string is no-op.
    """
    if isinstance(value, (list, tuple, set)):
        value = ','.join(value)
    return value


def prepare_attachments(attachment):
    """
    Converts incoming attachment into dictionary.
    """
    if isinstance(attachment, tuple):
        attachment = {
            'Name': attachment[0],
            'Content': attachment[1],
            'ContentType': attachment[2],
        }
    elif isinstance(attachment, MIMEBase):
        attachment = {
            'Name': attachment.get_filename(),
            'Content': attachment.get_payload(),
            'ContentType': attachment.get_content_type(),
        }
    return attachment


class Email(Model):

    def __init__(self, **kwargs):
        assert kwargs.get('TextBody') or kwargs.get('HtmlBody'), 'Provide either email TextBody or HtmlBody or both'
        if not kwargs.get('Headers'):
            kwargs['Headers'] = {}
        if not kwargs.get('Attachments'):
            kwargs['Attachments'] = []
        super(Email, self).__init__(**kwargs)

    def __setitem__(self, key, value):
        self.Headers[key] = value

    def __delitem__(self, key):
        del self.Headers[key]

    @classmethod
    def from_mime(cls, message, manager):
        """
        Instantiates ``Email`` instance from ``MIMEText`` instance.

        :param message: ``email.mime.text.MIMEText`` instance.
        :param manager: :py:class:`EmailManager` instance.
        :return: :py:class:`Email`
        """
        return cls(manager=manager, From=message['From'], To=message['To'], TextBody=message.get_payload(),
                   Subject=message['Subject'], Cc=message['Cc'], Bcc=message['Bcc'], ReplyTo=message['Reply-To'])

    def as_dict(self):
        """
        Additionally encodes headers.

        :return:
        """
        data = super(Email, self).as_dict()
        data['Headers'] = [{'Name': name, 'Value': value} for name, value in data['Headers'].items()]
        for field in ('To', 'Cc', 'Bcc'):
            if field in data:
                data[field] = list_to_csv(data[field])
        data['Attachments'] = [prepare_attachments(attachment) for attachment in data['Attachments']]
        return data

    def attach(self, *payloads):
        """
        Appends given payloads to current payload.

        :param payloads:
        :type payloads: `dict`, `tuple`, `list`, `MIMEBase`
        :return: None.
        """
        self.Attachments.extend(payloads)

    def send(self):
        """
        Sends email.

        :return: Information about sent email.
        :rtype: `dict`
        """
        return self._manager._send(**self.as_dict())


class EmailBatch(Model):
    """
    Gathers multiple emails in a single batch.
    """

    def __init__(self, *emails, **kwargs):
        self.emails = emails
        super(EmailBatch, self).__init__(**kwargs)

    def __len__(self):
        return len(self.emails)

    def as_dict(self):
        """
        Converts all available emails to dictionaries.

        :return: List of dictionaries.
        """
        return [self._construct_email(email) for email in self.emails]

    def _construct_email(self, email):
        """
        Converts incoming data to properly structured dictionary.
        """
        if isinstance(email, dict):
            email = Email(manager=self._manager, **email)
        elif isinstance(email, MIMEText):
            email = Email.from_mime(email, self._manager)
        elif not isinstance(email, Email):
            raise ValueError
        return email.as_dict()

    def send(self):
        """
        Sends email batch.

        :return: Information about sent emails.
        :rtype: `list`
        """
        return self._manager._send_batch(*self.as_dict())


class EmailManager(ModelManager):
    """
    Sends emails via Postmark REST API.
    """
    name = 'emails'

    def _send(self, **kwargs):
        """
        Low-level send call. Does not apply any transformation to given data.
        """
        return self._call('POST', '/email', data=kwargs).json()

    def _send_batch(self, *emails):
        """
        Low-level batch send call.
        """
        return self._call('POST', '/email/batch', data=emails).json()

    def send(self, message=None, From=None, To=None, Cc=None, Bcc=None, Subject=None, Tag=None, HtmlBody=None,
             TextBody=None, ReplyTo=None, Headers=None, TrackOpens=None, Attachments=None):
        """
        Sends single email.

        :param message: :py:class:`Email` or ``email.mime.text.MIMEText`` instance.
        :param str From: The sender email address.
        :param To: Recipient email address.
                   Multiple recipients could be specified as list or string with comma separated values.
        :type To: str or list
        :param Cc: Cc recipient email address.
                   Multiple Cc recipients could be specified as list or string with comma separated values.
        :type Cc: str or list
        :param Bcc: Bcc recipient email address.
                    Multiple Bcc recipients could be specified as list or string with comma separated values.
        :type Bcc: str or list
        :param str Subject: Email subject.
        :param str Tag: Email tag.
        :param str HtmlBody: HTML email message.
        :param str TextBody: Plain text email message.
        :param str ReplyTo: Reply To override email address.
        :param dict Headers: Dictionary of custom headers to include.
        :param bool TrackOpens: Activate open tracking for this email.
        :param list Attachments: List of attachments.
        :return: Information about sent email.
        :rtype: `dict`
        """
        assert (not (message and (From or To))), 'You should specify either message or From and To parameters'
        if message is None:
            message = self.Email(From=From, To=To, Cc=Cc, Bcc=Bcc, Subject=Subject, Tag=Tag, HtmlBody=HtmlBody,
                                 TextBody=TextBody, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens,
                                 Attachments=Attachments)
        elif isinstance(message, MIMEText):
            message = Email.from_mime(message, self)
        elif not isinstance(message, Email):
            raise TypeError('message should be either Email or MIMEText instance')
        return message.send()

    def send_batch(self, *emails):
        """
        Sends email batch.

        :param emails: :py:class:`Email` instances or dictionaries
        """
        return self.EmailBatch(*emails).send()

    # NOTE. The following methods are included here to expose better interface without need to import relevant classes.

    def Email(self, From, To, Cc=None, Bcc=None, Subject=None, Tag=None, HtmlBody=None, TextBody=None, ReplyTo=None,
              Headers=None, TrackOpens=None, Attachments=None):
        """
        Constructs :py:class:`Email` instance.

        :return: :py:class:`Email`
        """
        return Email(manager=self, From=From, To=To, Cc=Cc, Bcc=Bcc, Subject=Subject, Tag=Tag, HtmlBody=HtmlBody,
                     TextBody=TextBody, ReplyTo=ReplyTo, Headers=Headers, TrackOpens=TrackOpens,
                     Attachments=Attachments)

    def EmailBatch(self, *emails):
        """
        Constructs :py:class:`EmailBatch` instance.

        :return: :py:class:`EmailBatch`
        """
        return EmailBatch(*emails, manager=self)
