.. _triggers:

Inbound rules triggers
======================

The Inbound rules triggers API is available via the ``triggers.inboundrules`` manager.

.. code-block:: python

    >>> postmark.triggers.inboundrules.all()
    [<InboundRule: 962286>, ...]

Tags triggers
=============

The Tags triggers API is available via the ``triggers.tags`` manager.

.. code-block:: python

    >>> postmark.triggers.tags.all()
    [<Tag: welcome>, ...]
