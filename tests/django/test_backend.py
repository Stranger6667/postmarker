# coding: utf-8
from __future__ import unicode_literals

import pytest
from django import VERSION
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, send_mail
from requests import Response

from postmarker.core import TEST_TOKEN
from postmarker.django import EmailBackend
from postmarker.django.signals import post_send, pre_send
from postmarker.models.emails import Email


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
        'Tag': None,
        'TrackOpens': False,
        'From': 'sender@example.com'
    }, )
    assert patched_request.call_args[1]['headers']['X-Postmark-Server-Token'] == settings.POSTMARK['TOKEN']


def test_send_mail_with_attachment(patched_request):
    """
    Test sending email with attachment

    The Django backend crashes when sending an email with an attachment.
    https://github.com/Stranger6667/postmarker/issues/98

    This test does not send any mail. Instead, it demonstrates the bug by
    constructing the same underlying datastructures that the backend would
    construct.
    """
    msg = EmailMultiAlternatives(
        subject='subject', body='text_content', from_email='sender@example.com',
        to=['receiver@example.com'])
    msg.attach('hello.txt', 'Hello World', 'text/plain')
    msg.send()
    assert patched_request.call_args[1]['json'][0] == {
        'TextBody': 'text_content',
        'Attachments': [
            {
                'Name': 'hello.txt',
                'Content': 'Hello World',
                'ContentType': 'text/plain',
            }
        ],
        'From': 'sender@example.com',
        'HtmlBody': None,
        'ReplyTo': None,
        'Subject': 'subject',
        'To': 'receiver@example.com',
        'Headers': [],
        'TrackOpens': False,
        'Cc': None,
        'Bcc': None,
        'Tag': None
    }


def test_headers_encoding(patched_request):
    kwargs = {
        'subject': 'Тест',
        'message': 'Here is the message.',
        'from_email': 'Тест <sender@example.com>',
        'recipient_list': ['Тест <receiver@example.com>', 'Тест2 <receiver@example.com>']
    }
    send_mail(**kwargs)
    request = patched_request.call_args[1]['json'][0]
    assert request['Subject'] == kwargs['subject']
    assert request['From'] == kwargs['from_email']
    assert request['To'] == ', '.join(kwargs['recipient_list'])


@pytest.mark.skipif(
    VERSION[:2] < (1, 7),
    reason='Django < 1.7 does not support `html_message` argument in `send_mail` function.'
)
@pytest.mark.parametrize('html_message', (
    '<html></html>',
    '<html>Тест</html>',
    '''<html>
       <body>
           <div>
             %s
           </div>
       </body>
       </html>''' % ('.' * 1000)
))
def test_send_mail_html_message(html_message, patched_request):
    send_mail(html_message=html_message, **SEND_KWARGS)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject here',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': 'Here is the message.',
        'HtmlBody': html_message,
        'TrackOpens': False,
        'Tag': None,
        'From': 'sender@example.com'
    }, )


def test_send_long_text_line(patched_request):
    kwargs = SEND_KWARGS.copy()
    message = 'A' * 1000
    kwargs['message'] = message
    send_mail(**kwargs)
    assert patched_request.call_args[1]['json'] == ({
        'ReplyTo': None,
        'Subject': 'Subject here',
        'To': 'receiver@example.com',
        'Bcc': None,
        'Headers': [],
        'Cc': None,
        'Attachments': [],
        'TextBody': message,
        'HtmlBody': None,
        'TrackOpens': False,
        'Tag': None,
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
        'Tag': None,
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
        'Tag': None,
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


@pytest.mark.usefixtures('patched_request')
class TestSignals:

    def test_pre_send(self, catch_signal):
        with catch_signal(pre_send) as handler:
            send_mail(**SEND_KWARGS)
        assert handler.called
        kwargs = handler.call_args[1]
        assert kwargs['sender'] == EmailBackend
        assert kwargs['signal'] == pre_send
        assert len(kwargs['messages']) == 1
        message = kwargs['messages'][0]
        assert Email.from_mime(message, None).as_dict() == {
            'Attachments': [],
            'Bcc': None,
            'Cc': None,
            'From': 'sender@example.com',
            'Headers': [],
            'HtmlBody': None,
            'ReplyTo': None,
            'Subject': 'Subject here',
            'Tag': None,
            'TextBody': 'Here is the message.',
            'To': 'receiver@example.com'
        }

    def test_post_send(self, catch_signal, patched_request):
        patched_request.return_value = Response()
        patched_request.return_value.status_code = 200
        patched_request.return_value._content = b'[{"ErrorCode": 0, "To": "receiver@example.com", "SubmittedAt": ' \
                                                b'"2016-10-06T10:05:30.570118-04:00", "Message": "Test job accepted",' \
                                                b' "MessageID": "96a981da-9b7c-4aa9-bda2-84ab99097686"}]'
        with catch_signal(post_send) as handler:
            send_mail(**SEND_KWARGS)
        assert handler.called
        kwargs = handler.call_args[1]
        assert kwargs['sender'] == EmailBackend
        assert kwargs['signal'] == post_send
        assert kwargs['response'] == [{
            'ErrorCode': 0,
            'Message': 'Test job accepted',
            'MessageID': '96a981da-9b7c-4aa9-bda2-84ab99097686',
            'SubmittedAt': '2016-10-06T10:05:30.570118-04:00',
            'To': 'receiver@example.com'
        }]
