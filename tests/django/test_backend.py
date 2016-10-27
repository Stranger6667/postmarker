# coding: utf-8
import pytest
from django import VERSION
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail

from postmarker.core import TEST_TOKEN


pytestmark = pytest.mark.usefixtures('outbox')


SEND_KWARGS = {
    'subject': 'Subject here',
    'message': 'Here is the message.',
    'from_email': 'sender@example.com',
    'recipient_list': ['receiver@example.com']
}


def send_with_connection(connection):
    mail.EmailMessage(
        'Subject', 'Body', 'sender@example.com', ['receiver@example.com'],
        connection=connection,
    ).send()


def test_send_mail(patched_request, settings):
    send_mail(**SEND_KWARGS)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject here',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': 'Here is the message.',
        'HtmlBody': None,
        'TrackOpens': False,
        'From': 'sender@example.com'
    }, )
    assert patched_request.call_args[1]['headers']['X-Postmark-Server-Token'] == settings.POSTMARK['TOKEN']


def test_unicode_header(patched_request):
    kwargs = SEND_KWARGS.copy()
    kwargs['subject'] = 'Тест'
    send_mail(**kwargs)
    assert patched_request.call_args[1]['json'][0]['Subject'] == 'Тест'


@pytest.mark.skipif(
    VERSION[:2] < (1, 7),
    reason='Django < 1.7 does not support `html_message` argument in `send_mail` function.'
)
def test_send_mail_html_message(patched_request):
    send_mail(html_message='<html></html>', **SEND_KWARGS)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject here',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': 'Here is the message.',
        'HtmlBody': '<html></html>',
        'TrackOpens': False,
        'From': 'sender@example.com'
    }, )


def test_missing_api_key(settings):
    settings.POSTMARK = {}
    with pytest.raises(ImproperlyConfigured) as exc:
        send_mail(**SEND_KWARGS)
    assert str(exc.value) == 'You should specify TOKEN to use Postmark email backend'


def test_test_mode(settings, patched_request):
    settings.POSTMARK = {'TEST_MODE': True}
    send_mail(**SEND_KWARGS)
    assert patched_request.call_args[1]['headers']['X-Postmark-Server-Token'] == TEST_TOKEN


def test_extra_options(settings, patched_request):
    settings.POSTMARK['TRACK_OPENS'] = True
    send_mail(**SEND_KWARGS)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject here',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': 'Here is the message.',
        'HtmlBody': None,
        'TrackOpens': True,
        'From': 'sender@example.com'
    },)


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason='Context manager protocol was added in Django 1.8')
def test_context_manager(patched_request):
    with mail.get_connection() as connection:
        send_with_connection(connection)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': 'Body',
        'HtmlBody': None,
        'TrackOpens': True,
        'From': 'sender@example.com'
    },)


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason='Context manager protocol was added in Django 1.8')
class TestExceptions:

    @pytest.fixture(autouse=True)
    def setup(self, patched_request):
        patched_request().json.side_effect = ValueError

    def test_silent_exception(self):
        with mail.get_connection(fail_silently=True) as connection:
            send_with_connection(connection)

    def test_loud_exception(self):
        with mail.get_connection() as connection:
            with pytest.raises(ValueError):
                send_with_connection(connection)


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason='Context manager protocol was added in Django 1.8')
def test_close_closed_connection():
    with mail.get_connection() as connection:
        connection.close()
