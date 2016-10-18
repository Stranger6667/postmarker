.. _server:

Server
======

The Server API is available via the ``server`` manager:

.. code-block:: python

    >>> server = postmark.server.get()
    >>> server.edit(TrackOpens=True)
