# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives
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
        self.client = None
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

    def open(self):
        if self.client is None:
            self.client = PostmarkClient(token=self.token)
            return True
        return False

    def close(self):
        try:
            if self.client is not None:
                self.client.session.close()
        finally:
            self.client = None

    def send_messages(self, email_messages):
        try:
            client_created = self.open()
            prepared_messages = [self.prepare_message(message) for message in email_messages]
            response = self.client.emails.send_batch(*prepared_messages, TrackOpens=self.get_option('TRACK_OPENS'))
            msg_count = len(response)
            if client_created:
                self.close()
            return msg_count
        except Exception:
            if not self.fail_silently:
                raise

    def prepare_message(self, message):
        instance = message.message()
        instance.tag = getattr(message, 'tag', None)
        return instance


class PostmarkEmailMixin(object):
    """
    Provides an ability to set tags on Django email instances.
    """

    def __init__(self, *args, **kwargs):
        self.tag = kwargs.pop('tag', None)
        super(PostmarkEmailMixin, self).__init__(*args, **kwargs)


class PostmarkEmailMessage(PostmarkEmailMixin, EmailMessage):
    pass


class PostmarkEmailMultiAlternatives(PostmarkEmailMixin, EmailMultiAlternatives):
    pass
