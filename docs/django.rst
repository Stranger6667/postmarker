.. _django:

Django email backend
====================

For convenience, Postmarker provides a Django email backend. To use it you have to update your project settings:


.. code-block:: python

    EMAIL_BACKEND = 'postmarker.django.EmailBackend'
    POSTMARK = {
        'TOKEN': '<YOUR POSTMARK SERVER TOKEN>',
        'TEST_MODE': False,
        'VERBOSITY': 0,
    }

That's it!

Example:

.. code-block:: python

    >>> from django.core.mail import send_mail
    >>> send_mail(
        'Subject here',
        'Here is the message.',
        'sender@example.com',
        ['receiver@example.com'],
        html_message='<html></html>'
    )

.. important

    Postmarker supports Django 2.2, 3.2, and 4.0

For testing purposes, there is the ``TEST_MODE`` option.
When it is set to ``True`` all interactions will be conducted with a special testing API token - ``POSTMARK_API_TEST``.

To globally turn on ``TrackOpens`` feature, set ``TRACK_OPENS`` to ``True``.

Messages
========

To mark messages with tags, add metadata, or specify the message stream, you could use ``postmarker.django.PostmarkEmailMessage`` /  ``postmarker.django.PostmarkEmailMultiAlternatives``
instead of ``EmailMessage`` / ``EmailMultiAlternatives`` from Django.
Example:

.. code-block:: python

    >>> from postmarker.django import PostmarkEmailMessage
    >>> PostmarkEmailMessage(
        'Subject', 'Body', 'sender@example.com', ['receiver@example.com'],
        tag='Test tag',
        metadata={
            "color":"blue",
            "client-id":"12345",
        },
        message_stream="example-message-stream"
    ).send()

You can get the same feature for your own classes with ``PostmarkEmailMixin``.

Signals
=======

There are three signals, which are emitted:

- ``postmarker.django.pre_send`` is emitted just before the send;
- ``postmarker.django.post_send`` is emitted just after the send;
- ``postmarker.django.on_exception`` is emitted in case of exception.

``pre_send`` and ``post_send`` signals contain ``messages`` kwarg which contains all MIME messages, that are sent.
``post_send`` signal has ``response`` kwargs, which contains decoded response from Postmark.
``on_exception`` contains not prepared email instances in ``raw_messages`` kwarg and exception instance in ``exception``.
