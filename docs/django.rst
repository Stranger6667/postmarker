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
For every supported Python version, the backend is tested on the latest Django release that supports given the Python version:

 - Python 2.6 - Django 1.6
 - Python 3.2, 3.3, PyPy3 - Django 1.8
 - Python 2.7, 3.4, 3.5, 3.6, PyPy - Django 1.10

But it should work for all Django versions from 1.4.

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

Note! The ``html_message`` argument is available only on Django 1.7+.
To use HTML content in Django < 1.7 you should use the ``django.core.mail.messages.EmailMultiAlternatives`` class directly.

For testing purposes, there is the ``TEST_MODE`` option.
When it is set to ``True`` all interactions will be conducted with a special testing API token - ``POSTMARK_API_TEST``.

To globally turn on ``TrackOpens`` feature, set ``TRACK_OPENS`` to ``True``.

Messages
========

To mark messages with tags you could use ``postmarker.django.PostmarkEmailMessage`` /  ``postmarker.django.PostmarkEmailMultiAlternatives``
instead of ``EmailMessage`` / ``EmailMultiAlternatives`` from Django.
Example:

.. code-block:: python

    >>> from postmarker.django import PostmarkEmailMessage
    >>> PostmarkEmailMessage(
        'Subject', 'Body', 'sender@example.com', ['receiver@example.com'],
        tag='Test tag'
    ).send()

You can get the same feature for your own classes with ``PostmarkEmailMixin``.

Signals
=======

There are two signals, which are emitted:

- ``postmarker.django.pre_send`` is emitted just before the send
- ``postmarker.django.post_send`` is emitted just after the send

Both signals contain ``messages`` kwarg which contains all MIME messages, that are sent.
``post_send`` signal has ``response`` kwargs, which contains decoded response from Postmark.
