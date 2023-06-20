.. _supression:

Suppression API
==============

You can manage Postmark's Suppression lists with a few simple calls:

To view the current suppression list:
.. code-block:: python

    >>> response = postmark.get_suppressions(stream_id="test")
    >>> print(response['Suppressions'])
    {
      "Suppressions":[
        {
          "EmailAddress":"address@wildbit.com",
          "SuppressionReason":"ManualSuppression",
          "Origin": "Recipient",
          "CreatedAt":"2019-12-17T08:58:33-05:00"
        },
        {
          "EmailAddress":"bounce.address@wildbit.com",
          "SuppressionReason":"HardBounce",
          "Origin": "Recipient",
          "CreatedAt":"2019-12-17T08:58:33-05:00"
        },
        {
          "EmailAddress":"spam.complaint.address@wildbit.com",
          "SuppressionReason":"SpamComplaint",
          "Origin": "Recipient",
          "CreatedAt":"2019-12-17T08:58:33-05:00"
        }
      ]
    }
You can filter this with  "SuppressionReason", "Origin", "todate", "fromdate", and "EmailAddress" lile:
.. code-block:: python

    >>> response = postmark.get_suppressions(stream_id="test", EmailAddress="address@wildbit.com")
    >>> print(response['Suppressions'])
    {
      "Suppressions":[
        {
          "EmailAddress":"address@wildbit.com",
          "SuppressionReason":"ManualSuppression",
          "Origin": "Recipient",
          "CreatedAt":"2019-12-17T08:58:33-05:00"
        }
      ]
    }
You can add a new suppression with:
.. code-block:: python

    >>> response = postmark.add_suppressions(stream_id="test", emails=["address@wildbit.com"])
    >>> print(response['Suppressions'])
    {
      "Suppressions":[
        {
          "EmailAddress":"good.address@wildbit.com",
          "Status":"Suppressed",
          "Message": null
        },
      ]
    }
You can delete a suppression with:
.. code-block:: python

    >>> response = postmark.delete_suppressions(stream_id="test", emails=["address@wildbit.com"])
    >>> print(response['Suppressions'])
    {
      "Suppressions":[
            {
          "EmailAddress":"address@wildbit.com",
          "Status":"Deleted",
          "Message": null
        }
      ]
    }
