# coding: utf-8
from ._compat import get_args
from .core import PostmarkClient


POSTMARK_SERVER_TOKEN = 'postmark_server_token'


class PostmarkMixin(object):

    @property
    def postmark_client(self):
        self.require_setting(POSTMARK_SERVER_TOKEN, 'Postmark client')
        if not hasattr(self, '_postmark_client'):
            self._postmark_client = PostmarkClient(**self.get_postmark_kwargs())
        return self._postmark_client

    def get_postmark_kwargs(self):
        return dict(
            (arg, self.settings['postmark_' + arg])
            for arg in get_args(PostmarkClient)
            if 'postmark_' + arg in self.settings
        )

    def send(self, *args, **kwargs):
        return self.postmark_client.emails.send(*args, **kwargs)

    def send_batch(self, *args, **kwargs):
        return self.postmark_client.emails.send_batch(*args, **kwargs)
