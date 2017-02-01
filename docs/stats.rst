.. _stats:

Stats
=====

The Stats API is available via the ``stats`` manager:

.. code-block:: python

    >>> postmark.stats.overview(fromdate='2017-02-01')
    {
        'BounceRate': 0.0,
        'Bounced': 0,
        'Opens': 50,
        'SMTPApiErrors': 0,
        'Sent': 93,
        'SpamComplaints': 0,
        'SpamComplaintsRate': 0.0,
        'TotalClicks': 0,
        'TotalTrackedLinksSent': 0,
        'Tracked': 93,
        'UniqueLinksClicked': 0,
        'UniqueOpens': 19,
        'WithClientRecorded': 13,
        'WithLinkTracking': 0,
        'WithOpenTracking': 93,
        'WithPlatformRecorded': 19,
        'WithReadTimeRecorded': 19
    }
    >>> postmark.stats.sends(fromdate='2017-02-01')
    {
        'Days': [
            {'Date': '2017-02-01', 'Sent': 2}
        ],
        'Sent': 2
    }
