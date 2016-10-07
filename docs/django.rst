.. _django:

Django email backend
====================

For convenience Postmarker provides Django email backend. To use it you have to update your project settings:


.. code-block:: python

    EMAIL_BACKEND = 'postmarker.django.EmailBackend'
    POSTMARK = {
        'TOKEN': '<YOUR POSTMARK SERVER TOKEN>',
        'TEST_MODE': False,
    }

That's it!
For every supported Python version backend is tested on latest Django release that supports given Python version:

 - Python 2.6 - Django 1.6
 - Python 3.3, PyPy3 - Django 1.8
 - Python 2.7, 3.4, 3.5, 3.6, PyPy - Django 1.10

But it should work for all Django versions since 1.4.


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

Note! ``html_message`` argument is available only on Django 1.7+.
To use HTML content in Django < 1.7 you should use ``django.core.mail.messages.EmailMultiAlternatives`` class directly.

For testing purposes there is ``TEST_MODE`` option.
When it is set to ``True`` all interactions will be done with special testing api token - ``POSTMARK_API_TEST``