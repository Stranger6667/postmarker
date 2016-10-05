# coding: utf-8
"""
This module provides basic ways to send emails.
"""
from .base import ModelManager


class EmailManager(ModelManager):
    """
    Sends emails via Postmark REST API.
    """
    name = 'emails'

    def send(self, From, To, Cc=None, Bcc=None, Subject=None, Tag=None, HtmlBody=None, TextBody=None, ReplyTo=None,
             Headers=None, TrackOpens=None, Attachments=None):
        """
        Sends single email.

        :param str From: The sender email address.
        :param To: Recipient email address.
        :type To: str or list
        :param Cc: Cc recipient email address.
        :type Cc: str or list
        :param Bcc: Bcc recipient email address.
        :type Bcc: str or list
        :param str Subject: Email subject.
        :param str Tag: Email tag.
        :param str HtmlBody: HTML email message.
        :param str TextBody: Plain text email message.
        :param str ReplyTo: Reply To override email address.
        :param list Headers: List of custom headers to include.
        :param bool TrackOpens: Activate open tracking for this email.
        :param list Attachments: List of attachments.
        :return: Information about sent email.
        :rtype: `dict`
        """
        data = {
            'From': From,
            'To': To,
            'Cc': Cc,
            'Bcc': Bcc,
            'Subject': Subject,
            'Tag': Tag,
            'HtmlBody': HtmlBody,
            'TextBody': TextBody,
            'ReplyTo': ReplyTo,
            'Headers': Headers,
            'TrackOpens': TrackOpens,
            'Attachments': Attachments
        }
        return self._call('POST', '/email', data=data).json()
