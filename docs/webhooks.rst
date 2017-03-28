.. _webhooks:

Webhooks
========

.. automodule:: postmarker.webhooks

Inbound
-------

Basic
~~~~~

Here is a simple wrapper around Postmarkapp inbound webhook data, which provides some useful helpers.
The webhook data could automatically decoded from JSON.

.. code-block:: python

    >>> from postmarker.webhooks import InboundWebhook
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> inbound = InboundWebhook(data)

Or you could use already parsed data:

.. code-block:: python

    >>> import ujson
    >>> parsed = ujson.loads(data)
    >>> inbound = InboundWebhook(json=parsed)

The interface is straightforward - all keys-value pairs in JSON data are attributes of the ``InboundWebhook``:

.. code-block:: python

    >>> inbound.From
    support@postmarkapp.com

To access the headers there is a simpler way:

.. code-block:: python

    >>> inbound['X-Spam-Status']
    No

Attachments
~~~~~~~~~~~

To access the attachments you could use the ``Attachments`` attribute of the ``InboundWebhook`` which returns a list
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

Delivery
--------

For delivery webhook there is another wrapper - ``DeliveryWebhook`` with the same interface as above:

.. code-block:: python

    >>> from postmarker.webhooks import DeliveryWebhook
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> hook = DeliveryWebhook(data)

Open
----

For open webhook there is another wrapper - ``OpenWebhook`` with the same interface as above:

.. code-block:: python

    >>> from postmarker.webhooks import OpenWebhook
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> hook = OpenWebhook(data)

Bounce
------

For bounce webhook processing there is ``Bounce`` constructor in ``bounces`` manager.
It constructs new ``Bounce`` instance from given JSON string.

.. code-block:: python

    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> bounce = postmarker.bounces.Bounce(data)
    >>> bounce.activate()
    'OK'

Another way to parse a bounce - use ``Bounce.from_json`` method:

.. code-block:: python

    >>> from postmarker.models.bounces import Bounce
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> bounce = Bounce.from_json(data)

But in this case, there is no possibility to work with the bounce - only parsed data will be available.
