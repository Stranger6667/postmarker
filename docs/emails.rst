.. _emails:

Emails
======

.. automodule:: postmarker.models.emails

Basic
~~~~~

Sending emails is super easy! Here is the simplest case:

.. code-block:: python

    >>> postmark.emails.send(
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

Or send ``MIMEText``/``MIMEMultipart`` instances:

.. code-block:: python

    >>> message = MIMEText('Text')
    >>> message['From'] = 'sender@example.com'
    >>> message['To'] = 'receiver@example.com'
    >>> postmark.emails.send(message=message)

To specify multiple recipients (or ``Cc`` / ``Bcc``) you could pass values as a list or string with comma separated values:

.. code-block:: python

    >>> postmark.emails.send(
        From='sender@example.com',
        To=['first@example.com', 'second@example.com'],  # The same as 'first@example.com, second@example.com'
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )

Headers could be specified as a dict:

.. code-block:: python

    >>> postmark.emails.send(
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
    # File path string. Content type will be detected automatically
    >>> msg_4 = '/home/user/readme.txt'

Note! Content should be encoded as Base64 string.
Then pass the attachments to :py:meth:`~postmarker.models.emails.EmailManager.send`:

.. code-block:: python

    >>> postmark.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
        Attachments=[msg_1, msg_2, msg_3, msg_4]
    )

Postmarker also supports inline images. Here are the possible usage options:

.. code-block:: python

    >>> tuple_image = ('image', 'content', 'image/png', 'cid:image@example.com')
    >>> mime = MIMEImage('test content', 'png', name='image1.png')
    >>> mime.add_header('Content-ID', '<image1@example.com>')
    >>> mime_inline = MIMEImage('test content', 'png', name='image3.png')
    >>> mime_inline.add_header('Content-ID', '<image3@example.com>')
    >>> mime_inline.add_header('Content-Disposition', 'inline', filename='image3.png')
    >>> postmark.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
        Attachments=[tuple_image, mime, mime_inline]
    )

To send email in a batch there is :py:meth:`~postmarker.models.emails.EmailManager.send_batch` method.

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

You can pass either :py:class:`Email`/``MIMEText``/``MIMEMultipart`` instances or dictionaries.
Additionally, you may pass extra keywords to use with every email in a batch.

The batch size is not limited, but if the batch has more than 500 emails, then before sending, it will be split into chunks of 500 emails.

Postmark provides an interface to send emails created with a template. Example of usage with Postmarker:

.. code-block:: python

    >>> postmark.emails.send_with_template(
        TemplateId=123,
        TemplateModel={'username': 'Test'}
        From='sender@example.com',
        To='receiver@example.com',
    )

Attachments and headers work in the same way as in basic email sending.

Advanced
~~~~~~~~

To get more flexibility it is possible to use :py:class:`Email` objects.
:py:class:`EmailManager` uses them internally to send emails. To instantiate one:

.. code-block:: python

    >>> email = postmark.emails.Email(
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

Also it is possible to remove the header:

.. code-block:: python

    >>> del email['X-Accept-Language']

To add an attachment to an email there is :py:meth:`~postmarker.models.emails.Email.attach` method.

.. code-block:: python

    >>> email.attach(msg_1)

To attach multiple attachments, pass them all to :py:meth:`~postmarker.models.emails.Email.attach`:

.. code-block:: python

    >>> email.attach(msg_1, msg_2, msg_3)

Also it is possible to attach binary data:

.. code-block:: python

    >>> content = b'test content'
    >>> email.attach_binary(content=content, filename='readme.txt')

Batches are available via the :py:meth:`~postmarker.models.emails.EmailManager.EmailBatch` constructor.

.. code-block:: python

    >>> batch = postmark.emails.EmailBatch(email)
    >>> len(batch)
    1
    >>> batch.send()

For now, batches expose a very limited interface - only :py:meth:`~postmarker.models.emails.EmailBatch.send` method and
length information via the ``len`` function.

Template batches are available via the :py:meth:`~postmarker.models.emails.EmailManager.EmailTemplateBatch` constructor.

.. code-block:: python

    >>> batch = postmark.emails.EmailTemplateBatch(template)
    >>> len(batch)
    1
    >>> batch.send()
