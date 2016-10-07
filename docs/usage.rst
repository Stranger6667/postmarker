.. _usage:

Usage
=====

At the first step you have to initialize the client with proper API token.
Postmarker provides two client classes - ``ServerClient`` for Server API and ``AccountClient`` for Account API.

.. code-block:: python

    from postmarker.core import ServerClient


    >>> server_client = ServerClient(token='API_TOKEN')


.. code-block:: python

    from postmarker.core import AccountClient


    >>> account_client = AccountClient(token='API_TOKEN')

Variables ``server_client`` and ``account_client`` from the examples above will be used in next examples.
By default logging is configured to be silent. To enable it pass ``verbosity`` to client instantiation:

.. code-block:: python

    >>> server_client = ServerClient(token='API_TOKEN', verbosity=3)

With ``verbosity=3`` every request and response will be logged to console.