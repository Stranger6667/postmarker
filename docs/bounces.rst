.. _bounces:

Bounces
=======

.. automodule:: postmarker.models.bounces

.. code-block:: python

    >>> postmark.bounces
    <BouncesManager>

You can get a list of bounces with :py:meth:`~postmarker.models.bounces.BounceManager.all` method:

.. code-block:: python

    >>> postmark.bounces.all()
    [<Bounce: 943247350>, <Bounce: 924829573>]

Every bounce instance is represented by its ID. You can directly get one.

.. code-block:: python

    >>> bounce = postmark.bounces.get(943247350)
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
