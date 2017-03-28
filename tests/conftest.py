# coding: utf-8
import os
from contextlib import contextmanager

import pytest

from betamax import Betamax
from betamax_serializers import pretty_json
from postmarker.core import PostmarkClient

from ._compat import Mock, patch
from .helpers import replace_real_credentials


Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

DEFAULT_SERVER_TOKEN = 'SERVER_TOKEN'
DEFAULT_ACCOUNT_TOKEN = 'ACCOUNT_TOKEN'
CASSETTE_DIR = 'tests/cassettes/'
SERVER_TOKEN = os.environ.get('SERVER_TOKEN', DEFAULT_SERVER_TOKEN)
ACCOUNT_TOKEN = os.environ.get('ACCOUNT_TOKEN', DEFAULT_ACCOUNT_TOKEN)


def pytest_addoption(parser):
    parser.addoption('--record', action='store_true', help='Runs cleanup for recording session')


def pytest_unconfigure(config):
    if config.getoption('--record'):
        replace_real_credentials(CASSETTE_DIR, SERVER_TOKEN, 'X-Postmark-Server-Token', DEFAULT_SERVER_TOKEN)
        replace_real_credentials(CASSETTE_DIR, ACCOUNT_TOKEN, 'X-Postmark-Account-Token', DEFAULT_ACCOUNT_TOKEN)


@pytest.yield_fixture(autouse=True, scope='module')
def betamax_recorder(request, postmark):
    """
    Module level Betamax recorder.
    """
    if request.config.getoption('--record'):
        record_mode = 'new_episodes'
    else:
        record_mode = 'none' if os.environ.get('TRAVIS') else 'once'
    cassette_name = getattr(request.node._obj, 'CASSETTE_NAME', 'default')
    vcr = Betamax(
        postmark.session,
        cassette_library_dir=CASSETTE_DIR,
        default_cassette_options={
            'preserve_exact_body_bytes': True,
            'serialize_with': 'prettyjson',
            'match_requests_on': ['uri', 'query', 'method'],
            'record_mode': record_mode
        }
    )
    with vcr.use_cassette(cassette_name):
        yield


@pytest.yield_fixture
def patched_request():
    """
    Mocks network requests.
    """
    with patch('postmarker.core.requests.Session.request') as patched:
        yield patched


@pytest.fixture(scope='session')
def server_token():
    return SERVER_TOKEN


@pytest.fixture(scope='session')
def account_token():
    return ACCOUNT_TOKEN


@pytest.fixture(scope='session')
def postmark(server_token, account_token):
    return PostmarkClient(token=server_token, account_token=account_token)


@pytest.fixture(scope='session')
def bounce(postmark):
    return postmark.bounces.get(723626745)


@pytest.fixture(scope='session')
def server(postmark):
    return postmark.server.get()


@pytest.fixture()
def email(postmark):
    return postmark.emails.Email(From='sender@example.com', To='receiver@example.com', TextBody='text')


@pytest.fixture
def email_batch(postmark, email):
    return postmark.emails.EmailBatch(email)


@pytest.fixture(scope='session')
def template(postmark):
    return postmark.templates.get(983381)


@pytest.fixture(scope='session')
def domain(postmark):
    return postmark.domains.get(64054)


@pytest.fixture(scope='session')
def outbound_message(postmark):
    return postmark.messages.outbound.all(count=1)[0]


@contextmanager
def _catch_signal(signal):
    handler = Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)


@pytest.fixture
def catch_signal():
    return _catch_signal


BOUNCE_WEBHOOK = '''{
  "ID": 42,
  "Type": "HardBounce",
  "TypeCode": 1,
  "Name": "Hard bounce",
  "Tag": "Test",
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "ServerId": 23,
  "Description": "The server was unable to deliver your message (ex: unknown user, mailbox not found).",
  "Details": "Test bounce details",
  "Email": "john@example.com",
  "From": "sender@example.com",
  "BouncedAt": "2014-08-01T13:28:10.2735393-04:00",
  "DumpAvailable": true,
  "Inactive": true,
  "CanActivate": true,
  "Subject": "Test subject"
}'''


@pytest.fixture
def bounce_webhook(postmark):
    return postmark.bounces.Bounce(json=BOUNCE_WEBHOOK)
