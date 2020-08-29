from .core import PostmarkClient

POSTMARK_SERVER_TOKEN = "postmark_server_token"


class PostmarkMixin:
    @property
    def postmark_client(self):
        self.require_setting(POSTMARK_SERVER_TOKEN, "Postmark client")
        if not hasattr(self, "_postmark_client"):
            self._postmark_client = PostmarkClient.from_config(self.settings)
        return self._postmark_client

    def send(self, *args, **kwargs):
        return self.postmark_client.emails.send(*args, **kwargs)

    def send_batch(self, *args, **kwargs):
        return self.postmark_client.emails.send_batch(*args, **kwargs)
