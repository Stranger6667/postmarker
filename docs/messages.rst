.. _messages:

Inbound messages
================

The inbound messages API is available via the ``messages.inbound`` manager:

.. code-block:: python

    >>> postmark.messages.inbound.all()
    [<InboundMessage: Blocked message from test@example.com>, ...]


There is a simple way to access the headers in the ``InboundMessage`` instance:

.. code-block:: python

    >>> inbound['X-Spam-Status']
    No

Attachments
~~~~~~~~~~~

To access the attachments you could use the ``Attachments`` attribute of the ``InboundMessage`` which returns a list
of attachments.

.. code-block:: python

    >>> inbound.Attachments
    [<Attachment: test.txt>]

The interface is the same - all keys-value pairs in JSON data are attributes of the ``Attachment``:

.. code-block:: python

    >>> attachment = inbound.Attachments[0]
    >>> attachment.Name
    test.txt

Besides it, you could do the following with attachments:

- Access the decoded content
- Check it length
- Save it locally
- Convert it to MIME instance

.. code-block:: python

    >>> len(attachment)
    45
    >>> attachment.decoded
    This is attachment contents, base-64 encoded.
    >>> attachment.save('/directory/to/save/')
    /directory/to/save/test.txt
    >>> attachment.as_mime()
    <email.mime.base.MIMEBase at 0x10424b7b8>

Outbound messages
=================

The outbound messages API is available via the ``messages.outbound`` manager:

.. code-block:: python

    >>> postmark.messages.outbound.all()
    [<OutboundMessage: Sent message to test@example.com>, ...]

Opens
=====

The opens API handler is located in ``messages.outbound.opens`` manager.

.. code-block:: python

    >>> postmark.messages.outbound.opens.all()
    [<Open: Open from test@example.com>, ...]
