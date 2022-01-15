from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.encoding import force_str
from django.utils.functional import partition

from ..core import TEST_TOKEN, PostmarkClient
from ..exceptions import PostmarkerException
from .signals import on_exception, post_send, pre_send

DEFAULT_CONFIG = {"TEST_MODE": False, "TRACK_OPENS": False, "VERBOSITY": 0}


class EmailBackend(BaseEmailBackend):
    """A wrapper that manages sending emails via Postmark API."""

    def __init__(self, token=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.client = None
        if self.get_option("TEST_MODE"):
            self.server_token = TEST_TOKEN
        else:
            self.server_token = token or self.get_option("TOKEN")
            if self.server_token is None:
                raise ImproperlyConfigured("You should specify TOKEN to use Postmark email backend")

    @property
    def config(self):
        return getattr(settings, "POSTMARK", DEFAULT_CONFIG)

    def get_option(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def open(self):
        if self.client is None:
            self.client = PostmarkClient(server_token=self.server_token, verbosity=self.get_option("VERBOSITY"))
            return True
        return False

    def close(self):
        try:
            if self.client is not None:
                self.client.session.close()
        finally:
            self.client = None

    def send_messages(self, email_messages):
        if not email_messages:
            return
        msg_count = 0
        try:
            client_created = self.open()
            prepared_messages = [self.prepare_message(message) for message in email_messages]
            pre_send.send_robust(self.__class__, messages=prepared_messages)
            responses = self.client.emails.send_batch(*prepared_messages, TrackOpens=self.get_option("TRACK_OPENS"))
            post_send.send_robust(self.__class__, messages=prepared_messages, response=responses)
            sent, not_sent = partition(lambda x: x["ErrorCode"] != 0, responses)
            msg_count = len(sent)
            if not_sent:
                self.raise_for_response(not_sent)
            if client_created:
                self.close()
        except Exception as exc:
            on_exception.send_robust(self.__class__, raw_messages=email_messages, exception=exc)
            if not self.fail_silently:
                raise
        return msg_count

    def raise_for_response(self, responses):
        """Constructs appropriate exception from list of responses and raises it."""
        exception_messages = [self.client.format_exception_message(response) for response in responses]
        if len(exception_messages) == 1:
            message = exception_messages[0]
        else:
            message = "[%s]" % ", ".join(exception_messages)
        raise PostmarkerException(message)

    def prepare_message(self, message):
        instance = message.message()
        instance.tag = getattr(message, "tag", None)
        instance.metadata = getattr(message, "metadata", None)
        instance.message_stream = getattr(message, "message_stream", None)
        if message.bcc:
            instance["Bcc"] = ", ".join(map(force_str, message.bcc))
        return instance


class PostmarkEmailMixin:
    """Provides an ability to set tags on Django email instances."""

    def __init__(self, *args, **kwargs):
        self.tag = kwargs.pop("tag", None)
        self.metadata = kwargs.pop("metadata", None)
        self.message_stream = kwargs.pop("message_stream", None)
        super().__init__(*args, **kwargs)


class PostmarkEmailMessage(PostmarkEmailMixin, EmailMessage):
    pass


class PostmarkEmailMultiAlternatives(PostmarkEmailMixin, EmailMultiAlternatives):
    pass
