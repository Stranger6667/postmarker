import pytest
from requests import Response
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from postmarker.tornado import PostmarkMixin

MOCK_SEND_BATCH_RESPONSE = (
    b'[{"ErrorCode": 0, "To": "receiver@example.com", "SubmittedAt": '
    b'"2016-10-06T10:05:30.570118-04:00", "Message": "Test job accepted",'
    b' "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686"}]'
)

MOCK_SEND_RESPONSE = (
    b'{"ErrorCode": 0, "To": "receiver@example.com", "SubmittedAt": '
    b'"2016-10-06T10:05:30.570118-04:00", "Message": "Test job accepted",'
    b' "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686"}'
)


class BaseHandler(PostmarkMixin, RequestHandler):
    def get(self):
        self.write(str(self.get_value()))


class Handler(BaseHandler):
    def get_value(self):
        return self.postmark_client.server_token


class MaxRetriesHandler(BaseHandler):
    def get_value(self):
        return self.postmark_client.max_retries


class SendHandler(BaseHandler):
    def get_value(self):
        return self.send(
            From="sender@example.com",
            To="receiver@example.com",
            Subject="Postmark test",
            HtmlBody="<html><body><strong>Hello</strong> dear Postmark user.</body></html>",
        )["Message"]


class SendBatchHandler(BaseHandler):
    def get_value(self):
        return self.send_batch(
            {
                "From": "sender@example.com",
                "To": "receiver@example.com",
                "Subject": "Postmark test",
                "HtmlBody": "<html><body><strong>Hello</strong> dear Postmark user.</body></html>",
            }
        )[0]["Message"]


class ReuseHandler(BaseHandler):
    def get_value(self):
        return self.postmark_client is self.postmark_client


class TestPostmarkMixin(AsyncHTTPTestCase):
    def get_app(self):
        return Application(
            [
                (r"/", Handler),
                (r"/send/", SendHandler),
                (r"/send_batch/", SendBatchHandler),
                (r"/reuse/", ReuseHandler),
                (r"/max_retries/", MaxRetriesHandler),
            ],
            postmark_server_token="Test token",
        )

    @pytest.fixture(autouse=True)
    def _postmark(self, postmark_request):
        postmark_request.return_value = Response()
        postmark_request.return_value.status_code = 200
        self.postmark_request = postmark_request

    def assert_response(self, url, content, expected):
        self.postmark_request.return_value._content = content
        response = self.fetch(url)
        assert response.code == 200
        assert response.body == expected

    def test_token(self):
        self.assert_response("/", b"", b"Test token")

    def test_send(self):
        self.assert_response("/send/", MOCK_SEND_RESPONSE, b"Test job accepted")

    def test_send_batch(self):
        self.assert_response("/send_batch/", MOCK_SEND_BATCH_RESPONSE, b"Test job accepted")

    def test_reuse_client(self):
        self.assert_response("/reuse/", b"", b"True")

    def test_default_options(self):
        """Check if default values were used to initialize postmark client."""
        self.assert_response("/max_retries/", b"", b"0")
