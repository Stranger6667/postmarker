.. _usage:

Usage
=====

For the first step you have to initialize the client with a proper API token.
Postmarker provides a single ``PostmarkClient`` class for Server and Account APIs.

.. code-block:: python

    from postmarker.core import PostmarkClient


    >>> postmark = PostmarkClient(token='API_TOKEN')

The variable ``postmark`` from the example above will be used in the next examples.
By default, logging is configured to be silent. To enable it, pass ``verbosity`` to client instantiation:

.. code-block:: python

    >>> postmark = PostmarkClient(token='API_TOKEN', verbosity=3)

With ``verbosity=3`` every request and response will be logged to the console.