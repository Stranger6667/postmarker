# coding: utf-8
import pytest


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


class TestPostmarkMixin:
    @pytest.fixture(autouse=True)
    def setup(self, http_client, base_url, postmark_request):
        self.http_client = http_client
        self.base_url = base_url
        self.postmark_request = postmark_request

    def assert_response(self, url, body):
        response = self.http_client.fetch(url)
        assert response.code == 200
        assert response.body == body

    def set_postmark_response(self, content):
        self.postmark_request.return_value._content = content

    @pytest.mark.parametrize(
        "url, response, expected",
        (
            ("", b"", b"Test token"),
            ("/send/", MOCK_SEND_RESPONSE, b"Test job accepted"),
            ("/send_batch/", MOCK_SEND_BATCH_RESPONSE, b"Test job accepted"),
        ),
    )
    def test_handlers(self, url, response, expected):
        self.set_postmark_response(response)
        self.assert_response(url, expected)

    def test_reuse_client(self):
        self.set_postmark_response("")
        self.assert_response("/reuse/", b"True")

    def test_default_options(self):
        """
        Check if default values were used to initialize postmark client
        """
        self.set_postmark_response("")
        self.assert_response("/max_retries/", b"0")
