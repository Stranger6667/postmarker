.. _server:

Server
======

Server API is available via ``ServerManager``:

.. code-block:: python

    >>> server = server_client.server.get()
    >>> server.edit(TrackOpens=True)
