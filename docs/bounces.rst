.. _bounces:

Bounces
=======

.. automodule:: postmarker.models.bounces

Examples
~~~~~~~~

.. code-block:: python

    >>> server_client.bounces
    <BouncesManager>

You can get a list of bounces with :py:meth:`~postmarker.models.bounces.BounceManager.all` method:

.. code-block:: python

    >>> server_client.bounces.all()
    [<Bounce: 943247350>, <Bounce: 924829573>]

Every bounce instance is represented by its ID. You can directly get one.

.. code-block:: python

    >>> bounce = server_client.bounces.get(943247350)
    >>> bounce
    <Bounce: 943247350>

Bounce could be activated.

.. code-block:: python

    >>> bounce.activate()
    'OK'

Or you can get SMTP dump if it is available.

.. code-block:: python

    >>> bounce.dump
    'A lot of text'

Available classes
~~~~~~~~~~~~~~~~~

All available classes are listed below.

.. autoclass:: postmarker.models.bounces.BounceManager
   :members:

.. autoclass:: postmarker.models.bounces.Bounce
   :members:
