.. _bounces:

Bounces
=======

.. automodule:: postmarker.models.bounces

.. code-block:: python

    >>> postmark.bounces
    <BouncesManager>

You can get a list of bounces with the :py:meth:`~postmarker.models.bounces.BounceManager.all` method:

.. code-block:: python

    >>> postmark.bounces.all()
    [<Bounce: 943247350>, <Bounce: 924829573>]

Default number of bounces, which will be returned is 500 to fit in single network request.
More than 500 items will be fetching in multiple network requests:

.. code-block:: python

    >>> postmark.bounces.all(count=1001)
    [<Bounce: 943247350>, <Bounce: 924829573>, ...]

Here it will be 3 network requests, single one is limited by 500 items.
To load all available data, pass `None` as `count` value.

Every bounce instance is represented by its ID. You can search be specifying the ID.

.. code-block:: python

    >>> bounce = postmark.bounces.get(943247350)
    >>> bounce
    <Bounce: 943247350>

Bounce could be activated.

.. code-block:: python

    >>> bounce.activate()
    'OK'

Or you can get an SMTP dump if it is available.

.. code-block:: python

    >>> bounce.dump
    'A lot of text'

Also, you can access to corresponding ``OutboundMessage`` instance via ``message`` property.


.. code-block:: python

    >>> bounce.message
    <Sent message to test@example.com>
