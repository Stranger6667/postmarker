.. _webhooks:

Webhooks
========

Inbound
-------

Basic
~~~~~

The webhook data could automatically decoded from JSON with ``postmark.messages.inbound.InboundMessage``.

.. code-block:: python

    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> inbound = postmark.messages.inbound.InboundMessage(data)

It works in the same way as a regular ``InboundMessage``.

Delivery
--------

For delivery webhook there is a wrapper - ``Delivery`` with the regular model interface as in any other model (e.g. ``InboundMessage``):

.. code-block:: python

    >>> from postmarker.models.emails import Delivery
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> hook = Delivery.from_json(data)
    >>> hook.Recipient
    john@example.com

Open
----

Opens could be processed by ``postmark.messages.outbound.opens.Open``:

.. code-block:: python

    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> open = postmark.messages.outbound.opens.Open(data)

Bounce
------

For bounce webhook processing there is ``Bounce`` constructor in ``bounces`` manager.
It constructs new ``Bounce`` instance from given JSON string.

.. code-block:: python

    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> bounce = postmark.bounces.Bounce(data)
    >>> bounce.activate()
    'OK'

Another way to parse a bounce - use ``Bounce.from_json`` method:

.. code-block:: python

    >>> from postmarker.models.bounces import Bounce
    >>> with open('/path/to/raw_content.json') as fd:
            data = fd.read()
    >>> bounce = Bounce.from_json(data)

But in this case, there is no possibility to work with the bounce - only parsed data will be available.
