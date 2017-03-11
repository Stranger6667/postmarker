.. _changelog:

Changelog
=========

0.8.0 - TBA
-----------

- Added an ability to download more than 500 items. `#70`_

0.7.2 - 11.03.2017
------------------

- Fixed Django backend crash with attachments. `#98`_

0.7.1 - 10.03.2017
------------------

- Added `VERBOSITY` option to the Django backend. `#92`_

0.7.0 - 02.03.2017
------------------

- Stats API. (`#72`_)
- Sender Signatures API. (`#73`_)
- Messages API. (`#71`_)
- Inbound webhook wrapper. (`#87`_)

0.6.2 - 02.01.2017
------------------

- Fixed Unicode string handling on Python 2. `#78`_

0.6.1 - 01.01.2017
------------------

- Fixed handling of `quoted-printable` payload. `#76`_

0.6.0 - 05.12.2016
------------------

- Support for link tracking. `#62`_
- Better exceptions handling. `#50`_
- Support for spam check API. `#57`_
- Inline images support. `#52`_
- Domains API. `#64`_

0.5.3 - 27.10.2016
------------------

- Tags for Django messages. `#59`_

0.5.2 - 27.10.2016
------------------

- Fixed headers decoding. `#60`_

0.5.1 - 18.10.2016
------------------

- Fixed invalid messages count in email batches. `#55`_
- Better Django support. `#51`_

0.5.0 - 15.10.2016
------------------

- Status API. `#39`_
- Add custom user agent. `#43`_
- Jython support. `#13`_
- Handle more than 500 emails in batches. `#46`_
- Templates API. `#15`_

0.4.0 - 09.10.2016
------------------

- Python 3.2 support. `#38`_
- Refactoring. ``ServerClient`` & ``AccountClient`` were removed. `#41`_

0.3.1 - 08.10.2016
------------------

- Move repo.

0.3.0 - 07.10.2016
------------------

- Pass extra settings to Django backend. `#29`_
- Testing feature for ``Django`` backend. `#27`_
- Logging. `#19`_
- Server API. `#14`_
- Improved attachments support. `#23`_
- Improved MIME messages support. `#28`_

0.2.0 - 07.10.2016
------------------

- Django email backend. `#16`_
- Support for ``MIMEText`` sending. `#25`_
- Batch emailing implementation. `#12`_
- Ability to remove headers from email message. `#24`_
- Improved attachments interface. `#18`_
- Support for sending single email. `#11`_

0.1.1 - 05.10.2016
------------------

- Fixed packaging issue

0.1.0 - 05.10.2016
------------------

- Initial release.


.. _#98: https://github.com/Stranger6667/postmarker/issues/98
.. _#92: https://github.com/Stranger6667/postmarker/issues/92
.. _#87: https://github.com/Stranger6667/postmarker/issues/87
.. _#78: https://github.com/Stranger6667/postmarker/issues/78
.. _#76: https://github.com/Stranger6667/postmarker/issues/76
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