# coding: utf-8
from functools import partial

import pytest
from requests import Response

from postmarker.tornado import PostmarkMixin
from tornado.web import Application, RequestHandler


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
            From='sender@example.com',
            To='receiver@example.com',
            Subject='Postmark test',
            HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
        )['Message']


class SendBatchHandler(BaseHandler):

    def get_value(self):
        return self.send_batch(
            {
                'From': 'sender@example.com',
                'To': 'receiver@example.com',
                'Subject': 'Postmark test',
                'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
            }
        )[0]['Message']


class ReuseHandler(BaseHandler):

    def get_value(self):
        return self.postmark_client is self.postmark_client


@pytest.fixture
def app():
    return Application(
        [
            (r'/', Handler),
            (r'/send/', SendHandler),
            (r'/send_batch/', SendBatchHandler),
            (r'/reuse/', ReuseHandler),
            (r'/max_retries/', MaxRetriesHandler),
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
