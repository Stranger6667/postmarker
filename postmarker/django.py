# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

from .core import TEST_TOKEN, PostmarkClient


DEFAULT_CONFIG = {
    'TEST_MODE': False,
    'TRACK_OPENS': False,
}


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages sending emails via Postmark API.
    """

    def __init__(self, token=None, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        if self.get_option('TEST_MODE'):
            self.token = TEST_TOKEN
        else:
            self.token = token or self.get_option('TOKEN')
            if self.token is None:
                raise ImproperlyConfigured('You should specify TOKEN to use Postmark email backend')

    @property
    def config(self):
        return getattr(settings, 'POSTMARK', DEFAULT_CONFIG)

    def get_option(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def send_messages(self, email_messages):
        postmark = PostmarkClient(token=self.token)
        prepared_messages = [message.message() for message in email_messages]
        return len(postmark.emails.send_batch(*prepared_messages, TrackOpens=self.get_option('TRACK_OPENS')))
