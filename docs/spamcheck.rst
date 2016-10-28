.. _spamcheck:

Spam check API
==============

You can use Postmark's SpamAssassin filter API with a simple call:

.. code-block:: python

    >>> response = postmark.spamcheck('Raw email dump')
    >>> print(response['report'])
    pts rule name               description
    ---- ---------------------- --------------------------------------------------
     1.3 RDNS_NONE              Delivered to internal network by a host with no rDNS
     1.0 BODY_URI_ONLY          Message body is only a URI in one line of text or for
                                an image
     2.0 URI_ONLY_MSGID_MALF    URI only + malformed message ID
    >>> print(response['score'])
    3.8
