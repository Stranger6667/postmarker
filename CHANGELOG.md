# Changelog

## [Unreleased](https://github.com/Stranger6667/postmarker/compare/v1.0...HEAD)

### Added

- Support for Python 3.11–3.15.
- Layout templates: `TemplateType` and `LayoutTemplate` on `templates.create`, `validate` and `all`, `LayoutTemplate` on `templates.edit`, and `templates.push` to copy templates between servers.
- `on_exception` signal exported from `postmarker.django`, next to `pre_send` and `post_send`. [#213](https://github.com/Stranger6667/postmarker/pull/213)
- Support for Django 5.2, 6.0 and 6.1.
- Message Streams API: `message_streams.all`, `get`, `create`, `edit`, `archive` and `unarchive`.
- Support for `email.message.EmailMessage` (the modern `email` API) wherever MIME messages are accepted.
- Suppressions API: `suppressions.all`, `create` and `delete` per message stream. [#197](https://github.com/Stranger6667/postmarker/issues/197)
- Type annotations and `py.typed` marker.

### Changed

- Attachment content from MIME parts sent as single-line base64, without MIME line breaks.
- Django email backend raising `ClientError` with Postmark's `error_code` (the first failure's for batches) instead of a plain `PostmarkerException`. [#177](https://github.com/Stranger6667/postmarker/issues/177)

### Removed

- Support for Python 3.6–3.9.

### Fixed

- `postmark_request.return_value` incorrectly being an internal sentinel on Python 3.11+ (it should be a configurable mock).
- `send_batch` and `send_template_batch` incorrectly raising an empty `ValueError` for a list of emails (it should explain to pass them as separate arguments). [#212](https://github.com/Stranger6667/postmarker/issues/212)
- Django email backend incorrectly failing with `ValueError` on Django 6.0+. [#221](https://github.com/Stranger6667/postmarker/issues/221)
- Text attachments from MIME messages, including the Django backend, incorrectly sent without base64 encoding, which Postmark rejects. [#189](https://github.com/Stranger6667/postmarker/issues/189)
- `all()` for bounces, messages and opens incorrectly requesting past Postmark's limit of 10,000 for count + offset, which Postmark rejects (it should stop at the limit). [#194](https://github.com/Stranger6667/postmarker/issues/194)
- Django email backend incorrectly emitting `RemovedInDjango2028Warning` for `fail_silently` on Django 6.1+.
- Django email backend incorrectly dropping the `MAILERS` alias on Django 6.1+, which hid unknown `OPTIONS`.
- `Email` and `EmailTemplate` string representation incorrectly showing `None` (it should show the sender and recipients). [#211](https://github.com/Stranger6667/postmarker/issues/211)

### Security

- Spam check requests incorrectly sending email content over plain HTTP (they should use HTTPS).

## [1.0](https://github.com/Stranger6667/postmarker/compare/v0.18.2...v1.0) - 2022-01-15

### Added

- Python 3.10 support.
- Django 4.0 support. [#200](https://github.com/Stranger6667/postmarker/issues/200)

### Removed

- Deprecated `yield_fixture` usage in postmarker's pytest plugin.

## [0.18.2](https://github.com/Stranger6667/postmarker/compare/v0.18.1...v0.18.2) - 2021-06-03

### Added

- Support subject search on outbound messages.

## [0.18.1](https://github.com/Stranger6667/postmarker/compare/v0.18.0...v0.18.1) - 2021-05-13

### Fixed

- Fix documentation config to update docs on ReadTheDocs. [#195](https://github.com/Stranger6667/postmarker/issues/195)

## [0.18.0](https://github.com/Stranger6667/postmarker/compare/v0.17.1...v0.18.0) - 2021-05-11

### Added

- Support for `batchWithTemplates`.

## [0.17.1](https://github.com/Stranger6667/postmarker/compare/v0.17.0...v0.17.1) - 2021-03-02

### Added

- `root_api_url` argument for `PostmarkClient`. It allows you to change the address used by `postmarker` for sending API calls.

> **Important:** Use `https://api-ssl-temp.postmarkapp.com/` if you'd like to test your application against the upcoming TLSv1 deprecation by Postmark. Example:
>
> ```python
> postmark = PostmarkClient(
>     server_token="SERVER_TOKEN",
>     account_token="ACCOUNT_TOKEN",
>     root_api_url="https://api-ssl-temp.postmarkapp.com/"
> )
> # Use the client as usual
> ```

## [0.17.0](https://github.com/Stranger6667/postmarker/compare/v0.16.0...v0.17.0) - 2020-12-22

### Fixed

- Make `TemplateID` not required if `TemplateAlias` is specified. [#179](https://github.com/Stranger6667/postmarker/issues/179)

### Removed

- Support for Python 3.5.

## [0.16.0](https://github.com/Stranger6667/postmarker/compare/v0.15.0...v0.16.0) - 2020-11-10

### Added

- `MessageStream` support when sending emails. [#190](https://github.com/Stranger6667/postmarker/pull/190)

## [0.15.0](https://github.com/Stranger6667/postmarker/compare/v0.14.1...v0.15.0) - 2020-08-30

### Removed

- Support for Python 2.7, 3.3, 3.4, PyPy2 and Jython.

## [0.14.1](https://github.com/Stranger6667/postmarker/compare/v0.14.0...v0.14.1) - 2020-03-31

### Added

- Support for `Metadata` option in `EmailTemplate`. [#184](https://github.com/Stranger6667/postmarker/pull/184)

## [0.14.0](https://github.com/Stranger6667/postmarker/compare/v0.13.1...v0.14.0) - 2020-02-10

### Added

- `verifydkim` and `verifyreturnpath` for domains API. [#183](https://github.com/Stranger6667/postmarker/pull/183)

## [0.13.1](https://github.com/Stranger6667/postmarker/compare/0.13.0...v0.13.1) - 2019-11-15

### Added

- Support for metadata in Django email backend. [#181](https://github.com/Stranger6667/postmarker/pull/181)

## [0.13.0](https://github.com/Stranger6667/postmarker/compare/0.12.2...0.13.0) - 2018-11-25

### Added

- Support for Python 3.7. [#170](https://github.com/Stranger6667/postmarker/issues/170)
- Support for <span class="title-ref">Metadata</span> option. [#168](https://github.com/Stranger6667/postmarker/issues/168)

### Changed

- Stream logs to <span class="title-ref">sys.stdout</span> by default. [#159](https://github.com/Stranger6667/postmarker/issues/159)

### Removed

- Support for Python 2.6, 3.2 and 3.3.

## [0.12.2](https://github.com/Stranger6667/postmarker/compare/0.12.1...0.12.2) - 2018-11-05

### Changed

- Make <span class="title-ref">mock</span> package optional on Python 2. [#158](https://github.com/Stranger6667/postmarker/issues/158), [#162](https://github.com/Stranger6667/postmarker/issues/162)

## [0.12.1](https://github.com/Stranger6667/postmarker/compare/0.12.0...0.12.1) - 2018-11-05

### Changed

- Better handling of exceptions that happen during response parsing. [#163](https://github.com/Stranger6667/postmarker/issues/163)

## [0.12.0](https://github.com/Stranger6667/postmarker/compare/0.11.3...0.12.0) - 2018-06-12

### Added

- Support for <span class="title-ref">TemplateAlias</span>. [#150](https://github.com/Stranger6667/postmarker/issues/150)

### Fixed

- Processing of alternatives together with attachments. [#148](https://github.com/Stranger6667/postmarker/issues/148)
- Processing of <span class="title-ref">message/rfc822</span> attachments.

## [0.11.3](https://github.com/Stranger6667/postmarker/compare/0.11.2...0.11.3) - 2017-11-08

### Added

- Ability to convert inbound messages to MIME instances. [#90](https://github.com/Stranger6667/postmarker/issues/90)

### Fixed

- Fix missed <span class="title-ref">mock</span> dependency for Python 2. [#145](https://github.com/Stranger6667/postmarker/issues/145)

## [0.11.2](https://github.com/Stranger6667/postmarker/compare/0.11.1...0.11.2) - 2017-05-14

### Added

- Alternative instantiation method - `from_config`.

## [0.11.1](https://github.com/Stranger6667/postmarker/compare/0.11.0...0.11.1) - 2017-05-10

### Added

- Test helpers. [#112](https://github.com/Stranger6667/postmarker/issues/112)

## [0.11.0](https://github.com/Stranger6667/postmarker/compare/0.10.1...0.11.0) - 2017-05-02

### Added

- `message` property for `Bounce`, `Delivery` and `Open` classes to access corresponding `OutboundMessage` instance. [#119](https://github.com/Stranger6667/postmarker/issues/119)
- An ability to control timeout and retries behaviour. [#82](https://github.com/Stranger6667/postmarker/issues/82)
- Signal for exceptions in Django backend. [#126](https://github.com/Stranger6667/postmarker/issues/126)
- Tornado helper. [#85](https://github.com/Stranger6667/postmarker/issues/85)

## [0.10.1](https://github.com/Stranger6667/postmarker/compare/0.10.0...0.10.1) - 2017-04-03

### Fixed

- Fix Bcc ignoring in Django backend. [#135](https://github.com/Stranger6667/postmarker/issues/135)

## [0.10.0](https://github.com/Stranger6667/postmarker/compare/0.9.2...0.10.0) - 2017-03-30

### Added

- Short-circuit send of empty batches in Django backend. [#123](https://github.com/Stranger6667/postmarker/issues/123)

### Changed

- `OutboundMessageManager.get_details` and `InboundMessageManager.get_details` were methods were renamed to `get`. Now they returns `OutboundMessage` and `InboundMessage` instances respectively. [#125](https://github.com/Stranger6667/postmarker/issues/125)
- Renamed `token` kwarg in <span class="title-ref">PostmarkClient</span> to `server_token`. [#130](https://github.com/Stranger6667/postmarker/issues/130)

### Fixed

- Fix counting of successfully sent messages in Django backend. [#122](https://github.com/Stranger6667/postmarker/issues/122)
- Propagate API exceptions in Django backend. [#128](https://github.com/Stranger6667/postmarker/issues/128)

## [0.9.2](https://github.com/Stranger6667/postmarker/compare/0.9.1...0.9.2) - 2017-03-29

### Fixed

- Remove stale files from the package.

## [0.9.1](https://github.com/Stranger6667/postmarker/compare/0.9.0...0.9.1) - 2017-03-29

### Fixed

- Fix packaging issue.

## [0.9.0](https://github.com/Stranger6667/postmarker/compare/0.8.1...0.9.0) - 2017-03-28

### Added

- Ability to load all items without specifying exact <span class="title-ref">count</span> value. [#106](https://github.com/Stranger6667/postmarker/issues/106)
- Delivery webhook wrapper. [#95](https://github.com/Stranger6667/postmarker/issues/95)
- Open webhook wrapper. [#96](https://github.com/Stranger6667/postmarker/issues/96)
- Bounce webhook wrapper. [#97](https://github.com/Stranger6667/postmarker/issues/97)

### Changed

- `postmarker.webhooks.InboundWebhook` class was superseded by `postmark.messages.inbound.InboundMessage` constructor, which works in the same way.

### Fixed

- Fix PyPI package display. [#116](https://github.com/Stranger6667/postmarker/issues/116)

## [0.8.1](https://github.com/Stranger6667/postmarker/compare/0.8.0...0.8.1) - 2017-03-15

### Fixed

- Fix needless requests when <span class="title-ref">count</span> is more than number of available items. [#107](https://github.com/Stranger6667/postmarker/issues/107)

## [0.8.0](https://github.com/Stranger6667/postmarker/compare/0.7.2...0.8.0) - 2017-03-13

### Added

- Ability to download more than 500 items. [#70](https://github.com/Stranger6667/postmarker/issues/70)
- <span class="title-ref">pre_send</span> and <span class="title-ref">post_send</span> Django signals. [#83](https://github.com/Stranger6667/postmarker/issues/83)
- Inbound rules triggers API. [#75](https://github.com/Stranger6667/postmarker/issues/75)
- Tags triggers API. [#74](https://github.com/Stranger6667/postmarker/issues/74)

### Changed

- Output logs stream to default `sys.stderr`. [#102](https://github.com/Stranger6667/postmarker/issues/102)

## [0.7.2](https://github.com/Stranger6667/postmarker/compare/0.7.1...0.7.2) - 2017-03-11

### Fixed

- Fix Django backend crash with attachments. [#98](https://github.com/Stranger6667/postmarker/issues/98)

## [0.7.1](https://github.com/Stranger6667/postmarker/compare/0.7.0...0.7.1) - 2017-03-10

### Added

- <span class="title-ref">VERBOSITY</span> option to the Django backend. [#92](https://github.com/Stranger6667/postmarker/issues/92)

## [0.7.0](https://github.com/Stranger6667/postmarker/compare/0.6.2...0.7.0) - 2017-03-02

### Added

- Stats API. ([#72](https://github.com/Stranger6667/postmarker/issues/72))
- Sender Signatures API. ([#73](https://github.com/Stranger6667/postmarker/issues/73))
- Messages API. ([#71](https://github.com/Stranger6667/postmarker/issues/71))
- Inbound webhook wrapper. ([#87](https://github.com/Stranger6667/postmarker/issues/87))

## [0.6.2](https://github.com/Stranger6667/postmarker/compare/0.6.1...0.6.2) - 2017-01-02

### Fixed

- Fix Unicode string handling on Python 2. [#78](https://github.com/Stranger6667/postmarker/issues/78)

## [0.6.1](https://github.com/Stranger6667/postmarker/compare/0.6.0...0.6.1) - 2017-01-01

### Fixed

- Fix handling of <span class="title-ref">quoted-printable</span> payload. [#76](https://github.com/Stranger6667/postmarker/issues/76)

## [0.6.0](https://github.com/Stranger6667/postmarker/compare/0.5.3...0.6.0) - 2016-12-05

### Added

- Link tracking support. [#62](https://github.com/Stranger6667/postmarker/issues/62)
- Spam check API support. [#57](https://github.com/Stranger6667/postmarker/issues/57)
- Inline images support. [#52](https://github.com/Stranger6667/postmarker/issues/52)
- Domains API. [#64](https://github.com/Stranger6667/postmarker/issues/64)

### Changed

- Better exceptions handling. [#50](https://github.com/Stranger6667/postmarker/issues/50)

## [0.5.3](https://github.com/Stranger6667/postmarker/compare/0.5.2...0.5.3) - 2016-10-27

### Added

- Tags for Django messages. [#59](https://github.com/Stranger6667/postmarker/issues/59)

## [0.5.2](https://github.com/Stranger6667/postmarker/compare/0.5.1...0.5.2) - 2016-10-27

### Fixed

- Fix headers decoding. [#60](https://github.com/Stranger6667/postmarker/issues/60)

## [0.5.1](https://github.com/Stranger6667/postmarker/compare/0.5.0...0.5.1) - 2016-10-18

### Fixed

- Fix invalid messages count in email batches. [#55](https://github.com/Stranger6667/postmarker/issues/55)

### Changed

- Better Django support. [#51](https://github.com/Stranger6667/postmarker/issues/51)

## [0.5.0](https://github.com/Stranger6667/postmarker/compare/0.4.0...0.5.0) - 2016-10-15

### Added

- Status API. [#39](https://github.com/Stranger6667/postmarker/issues/39)
- Custom user agent. [#43](https://github.com/Stranger6667/postmarker/issues/43)
- Jython support. [#13](https://github.com/Stranger6667/postmarker/issues/13)
- Handling more than 500 emails in batches. [#46](https://github.com/Stranger6667/postmarker/issues/46)
- Templates API. [#15](https://github.com/Stranger6667/postmarker/issues/15)

## [0.4.0](https://github.com/Stranger6667/postmarker/compare/0.3.1...0.4.0) - 2016-10-09

### Added

- Python 3.2 support. [#38](https://github.com/Stranger6667/postmarker/issues/38)

### Removed

- `ServerClient` & `AccountClient` were removed. [#41](https://github.com/Stranger6667/postmarker/issues/41)

## [0.3.1](https://github.com/Stranger6667/postmarker/compare/0.3.0...0.3.1) - 2016-10-08

### Changed

- Move repo.

## [0.3.0](https://github.com/Stranger6667/postmarker/compare/0.2.0...0.3.0) - 2016-10-07

### Added

- Pass extra settings to Django backend. [#29](https://github.com/Stranger6667/postmarker/issues/29)
- Testing feature for `Django` backend. [#27](https://github.com/Stranger6667/postmarker/issues/27)
- Logging. [#19](https://github.com/Stranger6667/postmarker/issues/19)
- Server API. [#14](https://github.com/Stranger6667/postmarker/issues/14)
- Improved attachments support. [#23](https://github.com/Stranger6667/postmarker/issues/23)
- Improved MIME messages support. [#28](https://github.com/Stranger6667/postmarker/issues/28)

## [0.2.0](https://github.com/Stranger6667/postmarker/compare/0.1.1...0.2.0) - 2016-10-07

### Added

- Django email backend. [#16](https://github.com/Stranger6667/postmarker/issues/16)
- Support for `MIMEText` sending. [#25](https://github.com/Stranger6667/postmarker/issues/25)
- Batch emailing implementation. [#12](https://github.com/Stranger6667/postmarker/issues/12)
- Ability to remove headers from email message. [#24](https://github.com/Stranger6667/postmarker/issues/24)
- Improved attachments interface. [#18](https://github.com/Stranger6667/postmarker/issues/18)
- Support for sending single email. [#11](https://github.com/Stranger6667/postmarker/issues/11)

## [0.1.1](https://github.com/Stranger6667/postmarker/compare/0.1.0...0.1.1) - 2016-10-05

### Fixed

- Fix packaging issue

## 0.1.0 - 2016-10-05

- Initial release.
