.. _django:

Django email backend
====================

For convenience Postmarker provides Django email backend. To use it you have to update your project settings:


.. code-block:: python

    EMAIL_BACKEND = 'postmarker.django.backend.EmailBackend'
    POSTMARK = {
        'TOKEN': '<YOUR POSTMARK SERVER TOKEN>'
    }

That's it!
For every supported Python version backend is tested on latest Django release that supports given Python version:

 - Python 2.6 - Django 1.6
 - Python 3.3, PyPy3 - Django 1.8
 - Python 2.7, 3.4, 3.5, 3.6, PyPy - Django 1.10

But it should work for all Django versions since 1.4.
