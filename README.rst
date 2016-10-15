Postmarker
==========

.. image:: https://travis-ci.org/Stranger6667/postmarker.svg?branch=master
   :target: https://travis-ci.org/Stranger6667/postmarker
   :alt: Build Status

.. image:: https://codecov.io/github/Stranger6667/postmarker/coverage.svg?branch=master
   :target: https://codecov.io/github/Stranger6667/postmarker?branch=master
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/postmarker/badge/?version=stable
   :target: http://postmarker.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

Python client library for `Postmark API <http://developer.postmarkapp.com/developer-api-overview.html>`_.

This library is in active development now. Contributions are very welcome!

Installation
============

Postmarker can be obtained with ``pip``::

    $ pip install postmarker

Example usage
=============

Send single email:

.. code-block:: python

    >>> from postmarker.core import PostmarkClient
    >>> postmark = PostmarkClient(token='API_TOKEN')
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
            From='sender@example.com',
            To='receiver@example.com',
            Subject='Postmark test',
            HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
        },
        {
            From='sender2@example.com',
            To='receiver2@example.com',
            Subject='Postmark test 2',
            HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
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

There are a lot of features available. Check it out in our documentation! Just a few of them:

- Support for sending Python email instances.
- Bounces, Templates, Status & Server API.
- Django email backend.

Documentation
=============

You can view documentation online at:

- https://postmarker.readthedocs.io/en/stable/

Or you can look at the docs/ directory in the repository.

Python support
==============

Postmarker supports Python 2.6, 2.7, 3.2, 3.3, 3.4, 3.5, 3.6, PyPy, PyPy3 and Jython.

Thanks
======

Big thanks to `Shmele <https://github.com/butorov>`_ and `lobziik <https://github.com/lobziik>`_ for their reviews and advices :)