.. _testing:

Testing
=======

Postmarker provides two `pytest` fixtures:

- `postmark_request` - to mock all requests to Postmark API.
- `postmark` - an instance of ``PostmarkClient`` with `postmark_request` fixture applied.
