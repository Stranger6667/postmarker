# Postmarker

[![Build](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml/badge.svg)](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml) [![Coverage](https://codecov.io/gh/Stranger6667/postmarker/branch/master/graph/badge.svg)](https://codecov.io/gh/Stranger6667/postmarker) [![Version](https://img.shields.io/pypi/v/postmarker.svg)](https://pypi.org/project/postmarker/) [![Python versions](https://img.shields.io/pypi/pyversions/postmarker.svg)](https://pypi.org/project/postmarker/) [![Docs](https://readthedocs.org/projects/postmarker/badge/?version=stable)](https://postmarker.readthedocs.io/en/stable/) [![License](https://img.shields.io/pypi/l/postmarker.svg)](https://opensource.org/licenses/MIT)

Python client for the [Postmark](https://postmarkapp.com) email API, with a Django email backend.

> [!NOTE]
> Postmarker keeps Postmark's field names: `From`, `HtmlBody`, `TemplateModel`, `MessageStream`.
> Copy any field from the [Postmark API docs](https://postmarkapp.com/developer) and pass it as is. There are no snake_case aliases.

## Installation

```
uv pip install postmarker
```

Add the `css-inline` extra to inline CSS into HTML emails:

```
uv pip install 'postmarker[css-inline]'
```

## Usage

```python
from postmarker.core import PostmarkClient

postmark = PostmarkClient(server_token="API_TOKEN")
postmark.emails.send(
    From="sender@example.com",
    To="receiver@example.com",
    Subject="Postmark test",
    HtmlBody="<strong>Hello</strong> dear Postmark user.",
)
```

Pass `POSTMARK_API_TEST` as the server token to test sending without delivering emails.

Send with a template:

```python
postmark.emails.send_with_template(
    TemplateAlias="welcome",
    TemplateModel={"name": "Jane"},
    From="sender@example.com",
    To="receiver@example.com",
)
```

Send a batch. Postmarker splits it into requests of 500 messages, Postmark's limit:

```python
responses = postmark.emails.send_batch(
    {"From": "sender@example.com", "To": "first@example.com", "Subject": "Hi", "TextBody": "Hello"},
    {"From": "sender@example.com", "To": "second@example.com", "Subject": "Hi", "TextBody": "Hello"},
)
# Postmark accepts or rejects each message separately
failed = [response for response in responses if response["ErrorCode"] != 0]
```

Add headers and attachments:

```python
email = postmark.emails.Email(
    From="sender@example.com",
    To="receiver@example.com",
    Subject="Report",
    TextBody="See the attached report.",
)
email["X-Accept-Language"] = "en-us, en"
email.attach("/home/user/report.pdf")
email.attach_binary(content=b"content", filename="readme.txt")
email.send()
```

A rejected request raises `ClientError` with Postmark's [error code](https://postmarkapp.com/developer/api/overview#error-codes):

```python
from postmarker.exceptions import ClientError

try:
    postmark.emails.send(From="sender@example.com", To="receiver@example.com", TextBody="Hello")
except ClientError as exc:
    print(exc.error_code)  # For example, 406 for an inactive recipient
```

## Django

```python
EMAIL_BACKEND = "postmarker.django.EmailBackend"
POSTMARK = {"TOKEN": "<YOUR POSTMARK SERVER TOKEN>"}
```

Django then sends `send_mail`, `EmailMessage` and emails from third-party apps through Postmark.
On Django 6.1+, use `MAILERS`. The [Django guide](https://postmarker.readthedocs.io/en/stable/django/) covers it, along with tags, metadata, message streams and signals.

## Testing

Postmarker ships a `postmark_request` pytest fixture. It mocks requests to Postmark and records what your code sent:

```python
def test_welcome_email(postmark_request):
    send_welcome_email("jane@example.com")
    assert postmark_request.call_args.kwargs["json"]["To"] == "jane@example.com"
```

## Features

- Server APIs: Emails, Templates with layouts, Bounces, Messages (inbound, outbound, opens and clicks), Message Streams, Suppressions, Server, Stats and Triggers.
- Account APIs: Domains, Sender signatures, Servers and pushing templates between servers.
- Status and Spam check APIs.
- Webhook wrappers: Inbound, Delivery, Open, Click, Bounce, Spam complaint and Subscription change.
- Sending `email.message.Message` instances.
- CSS inlining via [css-inline](https://github.com/Stranger6667/css-inline).
- Django email backend and Tornado helper.
- Type annotations, with a `py.typed` marker.

## Documentation

<https://postmarker.readthedocs.io/en/stable/>

## Python support

Postmarker supports CPython 3.10 to 3.15 and PyPy 3.11. The Django email backend supports Django 5.2, 6.0 and 6.1.
