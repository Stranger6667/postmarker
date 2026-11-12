from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .core import PostmarkClient

if TYPE_CHECKING:
    from tornado.web import RequestHandler as _Base
else:
    _Base = object

POSTMARK_SERVER_TOKEN = "postmark_server_token"


class PostmarkMixin(_Base):
    _postmark_client: PostmarkClient

    @property
    def postmark_client(self) -> PostmarkClient:
        self.require_setting(POSTMARK_SERVER_TOKEN, "Postmark client")
        if not hasattr(self, "_postmark_client"):
            self._postmark_client = PostmarkClient.from_config(self.settings)
        return self._postmark_client

    def send(self, *args: Any, **kwargs: Any) -> Any:
        return self.postmark_client.emails.send(*args, **kwargs)

    def send_batch(self, *args: Any, **kwargs: Any) -> list[Any]:
        return self.postmark_client.emails.send_batch(*args, **kwargs)
