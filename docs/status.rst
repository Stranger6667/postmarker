.. _status:

Status
======

The Status API is available via the ``status`` manager:

.. code-block:: python

    >>> postmark.status.get()
    {'lastCheckDate': '2016-10-09T11:05:04Z', 'status': 'UP'}
    >>> postmark.status.services
    [
        {'status': 'UP', 'url': '/services/api', 'name': 'API Response Time'},
        {'status': 'UP', 'url': '/services/smtp', 'name': 'SMTP Response Time'},
        {'status': 'UP', 'url': '/services/web', 'name': 'Web Response Time'},
        {'status': 'UP', 'url': '/services/inbound', 'name': 'Inbound SMTP Response Time'}
    ]
    >>> postmark.status.availability
    {
        'fromDate': '2016-07-11T11:47:10.371Z',
        'percentageUp': 0.9998308505688754,
        'secondsDown': 5280,
        'secondsUp': 31209723,
        'toDate': '2016-10-09T11:47:10.372Z'
    }
    >>> postmark.status.delivery
    [
        {'missing': 0, 'spf': 1, 'spam': 0, 'inbox': 1, 'dkim': 1, 'name': 'AOL'},
        {'missing': 0, 'spf': 1, 'spam': 0, 'inbox': 1, 'dkim': 1, 'name': 'Apple'},
        {'missing': 0, 'spf': 1, 'spam': 0, 'inbox': 1, 'dkim': 1, 'name': 'Gmail'},
        {'missing': 0, 'spf': 1, 'spam': 0, 'inbox': 1, 'dkim': 1, 'name': 'Hotmail'},
        {'missing': 0, 'spf': 1, 'spam': 0, 'inbox': 1, 'dkim': 1, 'name': 'Yahoo!'}
    ]

Incidents are also available:

.. code-block:: python

    >>> postmark.incidents.last
    <Incident: 1965>
    >>> postmark.incidents.all
    [<Incident: 1965>, ...]
    >>> postmark.incidents.get(1965)
    <Incident: 1965>
