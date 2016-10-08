.. _usage:

Usage
=====

At the first step you have to initialize the client with proper API token.
Postmarker provides single ``PostmarkClient`` class for Server and Account APIs.

.. code-block:: python

    from postmarker.core import PostmarkClient


    >>> postmark = PostmarkClient(token='API_TOKEN')

Variables ``postmark`` from the examples above will be used in next examples.
By default logging is configured to be silent. To enable it pass ``verbosity`` to client instantiation:

.. code-block:: python

    >>> postmark = PostmarkClient(token='API_TOKEN', verbosity=3)

With ``verbosity=3`` every request and response will be logged to console.