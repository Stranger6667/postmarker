.. _supression:

Suppression API
==============

You can manage Postmark's Suppression lists with a few simple calls:

To view the current suppression list:
.. code-block:: python

    >>> response = postmark.get_suppressions(stream_id="test")
    >>> suppressions = (response['Suppressions'])
    >>> for suppression in suppressions:
    >>>    print(suppression.email_address])
    >>>    print("    " + suppression.suppression_reason])
    >>>    print("    " + suppression.origin])
    >>>    print("    " + suppression.created_at])
    address@wildbit.com
        ManualSuppression
        Recipient
        2019-12-17T08:58:33-05:00
    bounce.address@wilbit.com
        HardBounce
        Recipient
        2019-12-17T08:58:33-05:00
    spam.complaint.address@wildbit.com
        SpamComplaint
        Recipient
        2019-12-17T08:58:33-05:00
You can search for a particular suppression with  "emmails", "Origin", "todate", "fromdate", and "EmailAddress" lile:
.. code-block:: python

    >>> response = postmark.get_suppressions(stream_id="test", EmailAddress="address@wildbit.com")
    >>> print(response[0].email_address + " " + response[0].suppression_reason)
    address@wildbit.com ManualSuppression
You can add a new suppression with:
.. code-block:: python

    >>> response = postmark.add_suppressions(stream_id="test", emails=["address@wildbit.com"])
    >>> print(response[0].email_address + " " + response[0].status)
    good.address@wildbit.com Suppressed
You can delete a suppression with:
.. code-block:: python

    >>> response = postmark.delete_suppressions(stream_id="test", emails=["address@wildbit.com"])
    >>> print(response[0].email_address + " " + response[0].status)
    address@wildbit.com Deleted
