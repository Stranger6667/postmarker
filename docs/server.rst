.. _server:

Server
======

Server API is available via ``ServerManager``:

.. code-block:: python

    >>> server = postmark.server.get()
    >>> server.edit(TrackOpens=True)
