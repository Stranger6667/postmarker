.. _emails:

Emails
======

.. automodule:: postmarker.models.emails

Examples
~~~~~~~~

Sending emails is super easy!

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

Available classes
~~~~~~~~~~~~~~~~~

All available classes are listed below.

.. autoclass:: postmarker.models.emails.EmailManager
   :members: