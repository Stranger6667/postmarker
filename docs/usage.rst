.. _usage:

Usage
=====

General
-------

At the first step you have to initialize the client with proper API token.
Postmarker provides two client classes - ``ServerClient`` for Server API and ``AccountClient`` for Account API.

.. code-block:: python

    from postmarker.core import ServerClient


    >>> server_client = ServerClient(token='POSTMARK_API_TEST')


.. code-block:: python

    from postmarker.core import AccountClient


    >>> account_client = AccountClient(token='POSTMARK_API_TEST')

Variables ``server_client`` and ``account_client`` from the examples above will be used in next examples.
