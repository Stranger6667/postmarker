# coding: utf-8
from functools import partial

import pytest
from requests import Response

from postmarker.tornado import PostmarkMixin
from tornado.web import Application, RequestHandler


class Handler(PostmarkMixin, RequestHandler):

    def get(self):
        self.write(self.postmark_client.server_token)


class SendHandler(PostmarkMixin, RequestHandler):

    def get(self):
        response = self.send(
            From='sender@example.com',
            To='receiver@example.com',
            Subject='Postmark test',
            HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
        )
        self.write(response['Message'])


class SendBatchHandler(PostmarkMixin, RequestHandler):

    def get(self):
        response = self.send_batch(
            {
                'From': 'sender@example.com',
                'To': 'receiver@example.com',
                'Subject': 'Postmark test',
                'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
            }
        )
        self.write(response[0]['Message'])


class ReuseHandler(PostmarkMixin, RequestHandler):

    def get(self):
        self.write(str(self.postmark_client is self.postmark_client))


@pytest.fixture
def app():
    return Application(
        [
            (r'/', Handler),
            (r'/send/', SendHandler),
            (r'/send_batch/', SendBatchHandler),
            (r'/reuse/', ReuseHandler),
        ],
        postmark_server_token='Test token'
    )


@pytest.fixture
def patched_request(patched_request):
    patched_request.return_value = Response()
    patched_request.return_value.status_code = 200
    return patched_request


@pytest.fixture
def http_client(http_client, base_url):
    """
    Makes original http_client synchronous, to gather coverage data.
    """
    original_fetch = http_client.fetch

    def _fetch(url):
        fetch = partial(original_fetch, base_url + url)
        return http_client.io_loop.run_sync(fetch)

    http_client.fetch = _fetch
    return http_client
