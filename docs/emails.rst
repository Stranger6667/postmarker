.. _emails:

Emails
======

.. automodule:: postmarker.models.emails

Basic
~~~~~

Sending emails is super easy! Here is the most simple case:

.. code-block:: python

    >>> server_client.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )
    {'ErrorCode': 0,
     'Message': 'Test job accepted',
     'MessageID': 'fbff8f29-1742-48ee-93c2-f881c7049402',
     'SubmittedAt': '2016-10-05T06:51:08.9753663-04:00',
     'To': 'receiver@example.com'}

To specify multiple recipients (or ``Cc`` / ``Bcc``) you could pass values as list or string with comma separated values:

.. code-block:: python

    >>> server_client.emails.send(
        From='sender@example.com',
        To=['first@example.com', 'second@example.com'],  # The same as 'first@example.com, second@example.com'
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )

Headers could be specified as dict:

.. code-block:: python

    >>> server_client.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Headers={'X-Accept-Language': 'en-us, en'},
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )

Advanced
~~~~~~~~

To get more flexibility it is possible to use :py:class:`Email` objects.
:py:class:`EmailManager` uses them internally to send emails. To instantiate one:

.. code-block:: python

    >>> email = server_client.emails.Email(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )

Then send it:

.. code-block:: python

    >>> email.send()

To specify headers:

.. code-block:: python

    >>> email['X-Accept-Language'] = 'en-us, en'


Available classes
~~~~~~~~~~~~~~~~~

All available classes are listed below.

.. autoclass:: postmarker.models.emails.EmailManager
   :members:

.. autoclass:: postmarker.models.emails.Email
   :members: send