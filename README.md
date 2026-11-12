# Postmarker

[![Build](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml/badge.svg)](https://github.com/Stranger6667/postmarker/actions/workflows/build.yml) [![Coverage](https://codecov.io/gh/Stranger6667/postmarker/branch/master/graph/badge.svg)](https://codecov.io/gh/Stranger6667/postmarker) [![Version](https://img.shields.io/pypi/v/postmarker.svg)](https://pypi.org/project/postmarker/) [![Python versions](https://img.shields.io/pypi/pyversions/postmarker.svg)](https://pypi.org/project/postmarker/) [![Docs](https://readthedocs.org/projects/postmarker/badge/?version=stable)](https://postmarker.readthedocs.io/en/stable/) [![License](https://img.shields.io/pypi/l/postmarker.svg)](https://opensource.org/licenses/MIT)

Python client library for [Postmark API](http://developer.postmarkapp.com/developer-api-overview.html).

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
    HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
)
```

Send batch:

```python
>>> postmark.emails.send_batch(
    {
        'From': 'sender@example.com',
        'To': 'receiver@example.com',
        'Subject': 'Postmark test',
        'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
    },
    {
        'From': 'sender2@example.com',
        'To': 'receiver2@example.com',
        'Subject': 'Postmark test 2',
        'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
    }
)
```

Setup an email:

```python
>>> email = postmark.emails.Email(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
)
>>> email['X-Accept-Language'] = 'en-us, en'
>>> email.attach('/home/user/readme.txt')
>>> email.attach_binary(content=b'content', filename='readme.txt')
>>> email.send()
```

There are a lot of features available. Check it out in our documentation! Here's just a few of them:

- Support for sending Python email instances.
- Bounces, Domains, Messages, Templates, Sender signatures, Status, Stats & Server API.
- Django email backend.
- Tornado helper.
- Spam check API.
- Wrappers for Bounce, Inbound, Open and Delivery webhooks.

## Documentation

You can view the documentation online at:

- <https://postmarker.readthedocs.io/en/stable/>

Or you can look at the `docs/` directory in the repository.

## Python support

Postmarker supports CPython 3.10 - 3.15 and PyPy 3.11.

## Thanks

Many thanks to [Shmele](https://github.com/butorov) and [lobziik](https://github.com/lobziik) for their reviews and advice :)
