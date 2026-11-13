# Tornado helper

There is a mixin for [Tornado](http://www.tornadoweb.org/) support. You could implement request handler like this:

```python
from postmarker.tornado import PostmarkMixin
from tornado.web import RequestHandler


class EmailHandler(PostmarkMixin, RequestHandler):
    def post(self):
        # Awesome stuff here
        # ...
        # Send single email
        self.send(
            From="sender@example.com",
            To="receiver@example.com",
            Subject="Postmark test",
            HtmlBody="<strong>Hello</strong> dear Postmark user.",
        )
        # Send batch
        self.send_batch(
            {
                "From": "sender@example.com",
                "To": "receiver@example.com",
                "Subject": "Postmark test",
                "HtmlBody": "<strong>Hello</strong> dear Postmark user.",
            },
            {
                "From": "sender2@example.com",
                "To": "receiver2@example.com",
                "Subject": "Postmark test 2",
                "HtmlBody": "<strong>Hello</strong> dear Postmark user.",
            },
        )
        # Or do whatever you want to do with postmark
        bounces = self.postmark_client.bounces.all()
```

To make it work, define `postmark_server_token` option:

```python
from tornado.web import Application

app = Application(
    [
        (r"/send/", EmailHandler),
    ],
    postmark_server_token="YOUR_API_TOKEN",
)
```

And run your app! That's it. All possible options have the same name as in `PostmarkClient` prefixed with `postmark_`:

- `postmark_server_token`
- `postmark_account_token`
- `postmark_verbosity`
- `postmark_max_retries`
- `postmark_timeout`
- `postmark_inline_css`
