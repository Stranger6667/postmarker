.. _changelog:

Changelog
=========

`Unreleased`_
-------------

Added
~~~~~

- ``message`` property for ``Bounce``, ``Delivery`` and ``Open`` classes to access corresponding ``OutboundMessage`` instance. `#119`_
- An ability to control timeout and retries behaviour. `#82`_
- Signal for exceptions in Django backend. `#126`_
- Tornado helper. `#85`_

`0.10.1`_ - 2017-04-03
----------------------

Fixed
~~~~~

- Fix Bcc ignoring in Django backend. `#135`_

`0.10.0`_ - 2017-03-30
----------------------

Added
~~~~~

- Short-circuit send of empty batches in Django backend. `#123`_

Changed
~~~~~~~

- ``OutboundMessageManager.get_details`` and ``InboundMessageManager.get_details`` were methods were renamed to ``get``.
  Now they returns ``OutboundMessage`` and ``InboundMessage`` instances respectively. `#125`_
- Renamed ``token`` kwarg in `PostmarkClient` to ``server_token``. `#130`_

Fixed
~~~~~

- Fix counting of successfully sent messages in Django backend. `#122`_
- Propagate API exceptions in Django backend. `#128`_

`0.9.2`_ - 2017-03-29
---------------------

Fixed
~~~~~

- Remove stale files from the package.

`0.9.1`_ - 2017-03-29
---------------------

Fixed
~~~~~

- Fix packaging issue.

`0.9.0`_ - 2017-03-28
---------------------

Added
~~~~~

- Ability to load all items without specifying exact `count` value. `#106`_
- Delivery webhook wrapper. `#95`_
- Open webhook wrapper. `#96`_
- Bounce webhook wrapper. `#97`_

Changed
~~~~~~~

- ``postmarker.webhooks.InboundWebhook`` class was superseded by ``postmark.messages.inbound.InboundMessage`` constructor, which works in the same way.

Fixed
~~~~~

- Fix PyPI package display. `#116`_

`0.8.1`_ - 2017-03-15
---------------------

Fixed
~~~~~
- Fix needless requests when `count` is more than number of available items. `#107`_

`0.8.0`_ - 2017-03-13
---------------------

Added
~~~~~

- Ability to download more than 500 items. `#70`_
- `pre_send` and `post_send` Django signals. `#83`_
- Inbound rules triggers API. `#75`_
- Tags triggers API. `#74`_

Changed
~~~~~~~

- Output logs stream to default ``sys.stderr``. `#102`_

`0.7.2`_ - 2017-03-11
---------------------

Fixed
~~~~~

- Fix Django backend crash with attachments. `#98`_

`0.7.1`_ - 2017-03-10
---------------------

Added
~~~~~

- `VERBOSITY` option to the Django backend. `#92`_

`0.7.0`_ - 2017-03-02
---------------------

Added
~~~~~

- Stats API. (`#72`_)
- Sender Signatures API. (`#73`_)
- Messages API. (`#71`_)
- Inbound webhook wrapper. (`#87`_)

`0.6.2`_ - 2017-01-02
---------------------

Fixed
~~~~~
- Fix Unicode string handling on Python 2. `#78`_

`0.6.1`_ - 2017-01-01
---------------------

Fixed
~~~~~

- Fix handling of `quoted-printable` payload. `#76`_

`0.6.0`_ - 2016-12-05
---------------------

Added
~~~~~

- Link tracking support. `#62`_
- Spam check API support. `#57`_
- Inline images support. `#52`_
- Domains API. `#64`_

Changed
~~~~~~~

- Better exceptions handling. `#50`_

`0.5.3`_ - 2016-10-27
---------------------

Added
~~~~~

- Tags for Django messages. `#59`_

`0.5.2`_ - 2016-10-27
---------------------

Fixed
~~~~~

- Fix headers decoding. `#60`_

`0.5.1`_ - 2016-10-18
---------------------

Fixed
~~~~~

- Fix invalid messages count in email batches. `#55`_

Changed
~~~~~~~

- Better Django support. `#51`_

`0.5.0`_ - 2016-10-15
---------------------

Added
~~~~~

- Status API. `#39`_
- Custom user agent. `#43`_
- Jython support. `#13`_
- Handling more than 500 emails in batches. `#46`_
- Templates API. `#15`_

`0.4.0`_ - 2016-10-09
---------------------

Added
~~~~~
- Python 3.2 support. `#38`_

Removed
~~~~~~~
- ``ServerClient`` & ``AccountClient`` were removed. `#41`_

`0.3.1`_ - 2016-10-08
---------------------

Changed
~~~~~~~

- Move repo.

`0.3.0`_ - 2016-10-07
---------------------

Added
~~~~~

- Pass extra settings to Django backend. `#29`_
- Testing feature for ``Django`` backend. `#27`_
- Logging. `#19`_
- Server API. `#14`_
- Improved attachments support. `#23`_
- Improved MIME messages support. `#28`_

`0.2.0`_ - 2016-10-07
---------------------

Added
~~~~~

- Django email backend. `#16`_
- Support for ``MIMEText`` sending. `#25`_
- Batch emailing implementation. `#12`_
- Ability to remove headers from email message. `#24`_
- Improved attachments interface. `#18`_
- Support for sending single email. `#11`_

`0.1.1`_ - 2016-10-05
---------------------

Fixed
~~~~~

- Fix packaging issue

0.1.0 - 2016-10-05
------------------

- Initial release.

.. _Unreleased: https://github.com/Stranger6667/postmarker/compare/0.10.1...HEAD
.. _0.10.1: https://github.com/Stranger6667/postmarker/compare/0.10.0...0.10.1
.. _0.10.0: https://github.com/Stranger6667/postmarker/compare/0.9.2...0.10.0
.. _0.9.2: https://github.com/Stranger6667/postmarker/compare/0.9.1...0.9.2
.. _0.9.1: https://github.com/Stranger6667/postmarker/compare/0.9.0...0.9.1
.. _0.9.0: https://github.com/Stranger6667/postmarker/compare/0.8.1...0.9.0
.. _0.8.1: https://github.com/Stranger6667/postmarker/compare/0.8.0...0.8.1
.. _0.8.0: https://github.com/Stranger6667/postmarker/compare/0.7.2...0.8.0
.. _0.7.2: https://github.com/Stranger6667/postmarker/compare/0.7.1...0.7.2
.. _0.7.1: https://github.com/Stranger6667/postmarker/compare/0.7.0...0.7.1
.. _0.7.0: https://github.com/Stranger6667/postmarker/compare/0.6.2...0.7.0
.. _0.6.2: https://github.com/Stranger6667/postmarker/compare/0.6.1...0.6.2
.. _0.6.1: https://github.com/Stranger6667/postmarker/compare/0.6.0...0.6.1
.. _0.6.0: https://github.com/Stranger6667/postmarker/compare/0.5.3...0.6.0
.. _0.5.3: https://github.com/Stranger6667/postmarker/compare/0.5.2...0.5.3
.. _0.5.2: https://github.com/Stranger6667/postmarker/compare/0.5.1...0.5.2
.. _0.5.1: https://github.com/Stranger6667/postmarker/compare/0.5.0...0.5.1
.. _0.5.0: https://github.com/Stranger6667/postmarker/compare/0.4.0...0.5.0
.. _0.4.0: https://github.com/Stranger6667/postmarker/compare/0.3.1...0.4.0
.. _0.3.1: https://github.com/Stranger6667/postmarker/compare/0.3.0...0.3.1
.. _0.3.0: https://github.com/Stranger6667/postmarker/compare/0.2.0...0.3.0
.. _0.2.0: https://github.com/Stranger6667/postmarker/compare/0.1.1...0.2.0
.. _0.1.1: https://github.com/Stranger6667/postmarker/compare/0.1.0...0.1.1

.. _#135: https://github.com/Stranger6667/postmarker/issues/135
.. _#130: https://github.com/Stranger6667/postmarker/issues/130
.. _#128: https://github.com/Stranger6667/postmarker/issues/128
.. _#126: https://github.com/Stranger6667/postmarker/issues/126
.. _#125: https://github.com/Stranger6667/postmarker/issues/125
.. _#123: https://github.com/Stranger6667/postmarker/issues/123
.. _#122: https://github.com/Stranger6667/postmarker/issues/122
.. _#119: https://github.com/Stranger6667/postmarker/issues/119
.. _#116: https://github.com/Stranger6667/postmarker/issues/116
.. _#107: https://github.com/Stranger6667/postmarker/issues/107
.. _#106: https://github.com/Stranger6667/postmarker/issues/106
.. _#102: https://github.com/Stranger6667/postmarker/issues/102
.. _#98: https://github.com/Stranger6667/postmarker/issues/98
.. _#97: https://github.com/Stranger6667/postmarker/issues/97
.. _#96: https://github.com/Stranger6667/postmarker/issues/96
.. _#95: https://github.com/Stranger6667/postmarker/issues/95
.. _#92: https://github.com/Stranger6667/postmarker/issues/92
.. _#87: https://github.com/Stranger6667/postmarker/issues/87
.. _#85: https://github.com/Stranger6667/postmarker/issues/85
.. _#83: https://github.com/Stranger6667/postmarker/issues/83
.. _#82: https://github.com/Stranger6667/postmarker/issues/82
.. _#78: https://github.com/Stranger6667/postmarker/issues/78
.. _#76: https://github.com/Stranger6667/postmarker/issues/76
.. _#75: https://github.com/Stranger6667/postmarker/issues/75
.. _#74: https://github.com/Stranger6667/postmarker/issues/74
.. _#73: https://github.com/Stranger6667/postmarker/issues/73
.. _#72: https://github.com/Stranger6667/postmarker/issues/72
.. _#71: https://github.com/Stranger6667/postmarker/issues/71
.. _#70: https://github.com/Stranger6667/postmarker/issues/70
.. _#64: https://github.com/Stranger6667/postmarker/issues/64
.. _#62: https://github.com/Stranger6667/postmarker/issues/62
.. _#60: https://github.com/Stranger6667/postmarker/issues/60
.. _#59: https://github.com/Stranger6667/postmarker/issues/59
.. _#57: https://github.com/Stranger6667/postmarker/issues/57
.. _#55: https://github.com/Stranger6667/postmarker/issues/55
.. _#52: https://github.com/Stranger6667/postmarker/issues/52
.. _#51: https://github.com/Stranger6667/postmarker/issues/51
.. _#50: https://github.com/Stranger6667/postmarker/issues/50
.. _#46: https://github.com/Stranger6667/postmarker/issues/46
.. _#43: https://github.com/Stranger6667/postmarker/issues/43
.. _#41: https://github.com/Stranger6667/postmarker/issues/41
.. _#39: https://github.com/Stranger6667/postmarker/issues/39
.. _#38: https://github.com/Stranger6667/postmarker/issues/38
.. _#29: https://github.com/Stranger6667/postmarker/issues/29
.. _#28: https://github.com/Stranger6667/postmarker/issues/28
.. _#27: https://github.com/Stranger6667/postmarker/issues/27
.. _#25: https://github.com/Stranger6667/postmarker/issues/25
.. _#24: https://github.com/Stranger6667/postmarker/issues/24
.. _#23: https://github.com/Stranger6667/postmarker/issues/23
.. _#19: https://github.com/Stranger6667/postmarker/issues/19
.. _#18: https://github.com/Stranger6667/postmarker/issues/18
.. _#16: https://github.com/Stranger6667/postmarker/issues/16
.. _#15: https://github.com/Stranger6667/postmarker/issues/15
.. _#14: https://github.com/Stranger6667/postmarker/issues/14
.. _#13: https://github.com/Stranger6667/postmarker/issues/13
.. _#12: https://github.com/Stranger6667/postmarker/issues/12
.. _#11: https://github.com/Stranger6667/postmarker/issues/11
