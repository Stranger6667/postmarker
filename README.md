# Postmarker

[![Build](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml/badge.svg)](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml) [![Coverage](https://codecov.io/gh/Stranger6667/postmarker/branch/master/graph/badge.svg)](https://codecov.io/gh/Stranger6667/postmarker) [![Version](https://img.shields.io/pypi/v/postmarker.svg)](https://pypi.org/project/postmarker/) [![Python versions](https://img.shields.io/pypi/pyversions/postmarker.svg)](https://pypi.org/project/postmarker/) [![Docs](https://readthedocs.org/projects/postmarker/badge/?version=stable)](https://postmarker.readthedocs.io/en/stable/) [![License](https://img.shields.io/pypi/l/postmarker.svg)](https://opensource.org/licenses/MIT)

Python client library for [Postmark API](https://postmarkapp.com/developer).

## Installation

Postmarker can be obtained with `pip`:

```
pip install postmarker
```

## Usage example

**NOTE**:

The attributes of all classes are provided **as is**, without transformation to snake case. We don't want to introduce new names for existing entities.

Send single email:

```python
>>> from postmarker.core import PostmarkClient
>>> postmark = PostmarkClient(server_token='API_TOKEN')
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
```

Send batch:

```python
>>> postmark.emails.send_batch(
    {
        'From': 'sender@example.com',
        'To': 'receiver@example.com',
        'Subject': 'Postmark test',
        'HtmlBody': '<strong>Hello</strong> dear Postmark user.',
    },
    {
        'From': 'sender2@example.com',
        'To': 'receiver2@example.com',
        'Subject': 'Postmark test 2',
        'HtmlBody': '<strong>Hello</strong> dear Postmark user.',
    }
)
```

Setup an email:

```python
>>> email = postmark.emails.Email(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
>>> email['X-Accept-Language'] = 'en-us, en'
>>> email.attach('/home/user/readme.txt')
>>> email.attach_binary(content=b'content', filename='readme.txt')
>>> email.send()
```

There are a lot of features available. Check it out in our documentation! Here's just a few of them:

- Support for sending Python email instances.
- Server APIs: Bounces, Messages, Message Streams, Suppressions, Templates with layouts, Server, Stats and Triggers.
- Account APIs: Domains, Sender signatures, Servers and pushing templates between servers.
- Status API.
- CSS inlining for HTML emails via [css-inline](https://github.com/Stranger6667/css-inline).
- Django email backend.
- Tornado helper.
- Spam check API.
- Wrappers for Bounce, Inbound, Open and Delivery webhooks.
- `pytest` fixtures to mock Postmark API in tests.
- Type annotations, with a `py.typed` marker.

## Documentation

You can view the documentation online at:

- <https://postmarker.readthedocs.io/en/stable/>

Or you can look at the `docs/` directory in the repository.

## Python support

Postmarker supports CPython 3.10 - 3.15 and PyPy 3.11. The Django email backend supports Django 5.2, 6.0 and 6.1.

## Thanks

Many thanks to [Shmele](https://github.com/butorov) and [lobziik](https://github.com/lobziik) for their reviews and advice :)
