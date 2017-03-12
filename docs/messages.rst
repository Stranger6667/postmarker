.. _messages:

Inbound messages
================

The inbound messages API is available via the ``messages.inbound`` manager:

.. code-block:: python

    >>> postmark.messages.inbound.all()
    [<InboundMessage: Blocked message from test@example.com>, ...]

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
