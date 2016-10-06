# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

from .core import ServerClient


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages sending emails via Postmark API.
    """

    def __init__(self, token=None, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        postmark_config = getattr(settings, 'POSTMARK', {})
        self.token = token or postmark_config.get('TOKEN')
        if self.token is None:
            raise ImproperlyConfigured('You should specify TOKEN to use Postmark email backend')

    def send_messages(self, email_messages):
        server_client = ServerClient(token=self.token)
        prepared_messages = [message.message() for message in email_messages]
        return len(server_client.emails.send_batch(*prepared_messages))
