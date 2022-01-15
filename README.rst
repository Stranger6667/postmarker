Postmarker
==========

|Build| |Coverage| |Version| |Python versions| |Docs| |Chat| |License|

Python client library for `Postmark API <http://developer.postmarkapp.com/developer-api-overview.html>`_.

**Gitter**: https://gitter.im/Stranger6667/postmarker

Installation
============

Postmarker can be obtained with ``pip``::

    $ pip install postmarker

Usage example
=============

**NOTE**:

The attributes of all classes are provided **as is**, without transformation to snake case.
We don't want to introduce new names for existing entities.

Send single email:

.. code-block:: python

    >>> from postmarker.core import PostmarkClient
    >>> postmark = PostmarkClient(server_token='API_TOKEN')
    >>> postmark.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )

Send batch:

.. code-block:: python

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

Setup an email:

.. code-block:: python

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

There are a lot of features available. Check it out in our documentation! Here's just a few of them:

- Support for sending Python email instances.
- Bounces, Domains, Messages, Templates, Sender signatures, Status, Stats & Server API.
- Django email backend.
- Tornado helper.
- Spam check API.
- Wrappers for Bounce, Inbound, Open and Delivery webhooks.

Documentation
=============

You can view the documentation online at:

- https://postmarker.readthedocs.io/en/stable/

Or you can look at the docs/ directory in the repository.

Python support
==============

Postmarker supports CPython 3.6 - 3.10 and PyPy 3.7 & 3.8.

Thanks
======

Many thanks to `Shmele <https://github.com/butorov>`_ and `lobziik <https://github.com/lobziik>`_ for their reviews and advice :)

.. |Build| image:: https://github.com/Stranger6667/postmarker/workflows/build/badge.svg
   :target: https://github.com/Stranger6667/postmarker/actions
.. |Coverage| image:: https://codecov.io/github/Stranger6667/postmarker/coverage.svg?branch=master
    :target: https://codecov.io/github/Stranger6667/postmarker?branch=master
.. |Version| image:: https://img.shields.io/pypi/v/postmarker.svg
   :target: https://pypi.org/project/postmarker/
.. |Python versions| image:: https://img.shields.io/pypi/pyversions/postmarker.svg
   :target: https://pypi.org/project/postmarker/
.. |Docs| image:: https://readthedocs.org/projects/postmarker/badge/?version=stable
   :target: https://postmarker.readthedocs.io/en/stable/
   :alt: Documentation Status
.. |Chat| image:: https://img.shields.io/gitter/room/Stranger6667/postmarker.svg
   :target: https://gitter.im/Stranger6667/postmarker
   :alt: Gitter
.. |License| image:: https://img.shields.io/pypi/l/postmarker.svg
   :target: https://opensource.org/licenses/MIT
