.. _usage:

Usage
=====

For the first step you have to initialize the client with a proper API token.
Postmarker provides a single ``PostmarkClient`` class for Server and Account APIs.

.. code-block:: python

    from postmarker.core import PostmarkClient


    >>> postmark = PostmarkClient(server_token='SERVER_TOKEN', account_token='ACCOUNT_TOKEN')

The variable ``postmark`` from the example above will be used in the next examples.
By default, logging is configured to be silent. To enable it, pass ``verbosity`` to client instantiation:

.. code-block:: python

    >>> postmark = PostmarkClient(server_token='SERVER_TOKEN', account_token='ACCOUNT_TOKEN', verbosity=3)

With ``verbosity=3`` every request and response will be logged to the console.

By default logs are streamed to ``sys.stdout`` to be in line with the Twelve-Factor App. To change it you could use
``logs_stream`` parameter in ``PostmarkClient``.

For timeouts and max_retries handling there are two parameters - ``max_retries`` and ``timeout``.
The ``timeout`` value is passed to `requests.Session.request <http://docs.python-requests.org/en/master/api/#requests.Session.request>`_.
``max_retries`` is passed to `requests.adapters.HTTPAdapter <http://docs.python-requests.org/en/master/api/#requests.adapters.HTTPAdapter>`_.

Alternatively you could use ``PostmarkClient.from_config`` method, which is helpful to instantiate ``PostmarkClient``
from dict-like object, like Tornado or Flask configurations.

.. code-block:: python

    >>> config = {'POSTMARK_SERVER_TOKEN': 'foo', 'POSTMARK_TIMEOUT': 1}
    >>> postmark = PostmarkClient.from_config(config, is_uppercase=True)

With ``is_uppercase`` set to ``True`` keys will be converted to upper case before lookup in the config object.
The default value for ``is_uppercase`` is ``False``.
All arguments names from ``PostmarkClient.__init__`` will be looked up in the config object with default prefix `postmark_`.
To use different prefix, just pass ``prefix='my_prefix_'`` to ``PostmarkClient.from_config`` method.

.. code-block:: python

    >>> config = {'my_prefix_server_token': 'foo', 'my_prefix_timeout': 1}
    >>> postmark = PostmarkClient.from_config(config, prefix='my_prefix_')

If you want ``postmarker`` to send requests to a non-standard API url, use the ``root_api_url`` keyword argument to ``PostmarkClient``.

.. code-block:: python

    PostmarkClient(
        server_token='SERVER_TOKEN',
        account_token='ACCOUNT_TOKEN',
        root_api_url='https://api-ssl-temp.postmarkapp.com/'
    )
