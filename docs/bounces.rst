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
