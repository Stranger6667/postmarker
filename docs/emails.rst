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
     'Message': 'OK',
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

Attachments could be specified as a list of items in the following forms:

.. code-block:: python

    # Dictionary
    >>> msg_1 = {"Name": "readme.txt", "Content": "dGVzdCBjb250ZW50", "ContentType": "text/plain"}
    # Tuple
    >>> msg_2 = ("readme.txt", "dGVzdCBjb250ZW50", "text/plain")
    # MIMEBase instance
    >>> msg_3 = MIMEBase('text', 'plain')
    >>> msg_3.set_payload('dGVzdCBjb250ZW50')
    >>> msg_3.add_header('Content-Disposition', 'attachment', filename='readme.txt')

Note! Content should be encoded as Base64 string.
Then pass them to :py:meth:`~postmarker.models.emails.EmailManager.send`:

.. code-block:: python

    >>> server_client.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
        Attachments=[msg_1, msg_2, msg_3]
    )

To send email in batch there is :py:meth:`~postmarker.models.emails.EmailManager.send_batch` method.

.. code-block:: python

    >>> server_client.emails.send_batch(
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

You can pass either :py:class:`Email` instances or dictionaries.

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

Also it is possible to remove header:

.. code-block:: python

    >>> del email['X-Accept-Language']

To add an attachment to email there is :py:meth:`~postmarker.models.emails.Email.attach` method.

.. code-block:: python

    >>> email.attach(msg_1)

To attach multiple attachments pass them all to :py:meth:`~postmarker.models.emails.Email.attach`:

.. code-block:: python

    >>> email.attach(msg_1, msg_2, msg_3)

Batches are available via :py:meth:`~postmarker.models.emails.EmailManager.EmailBatch` constructor.

.. code-block:: python

    >>> batch = server_client.emails.EmailBatch(email)
    >>> len(batch)
    1
    >>> batch.send()

For now batches expose very limited interface - only :py:meth:`~postmarker.models.emails.EmailBatch.send` method and
length information via ``len`` function.
