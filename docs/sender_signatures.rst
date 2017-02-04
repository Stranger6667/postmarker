.. _sender_signatures:

Sender signatures
=================

The Sender signatures API is available via the ``senders`` manager:

.. code-block:: python

    >>> sender_signature = postmark.senders.get(128462)
    >>> sender_signature.delete()
