# coding: utf-8
import pytest
from django import VERSION
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail


def test_send_mail(patched_request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'sender@example.com',
        ['receiver@example.com'],
    )
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
        'From': 'sender@example.com'
    }, )


@pytest.mark.skipif(
    VERSION[:2] < (1, 7),
    reason='Django < 1.7 does not support `html_message` argument in `send_mail` function.'
)
def test_send_mail_html_message(patched_request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'sender@example.com',
        ['receiver@example.com'],
        html_message='<html></html>'
    )
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
        'From': 'sender@example.com'
    }, )


def test_missing_api_key(settings):
    settings.POSTMARK = {}
    with pytest.raises(ImproperlyConfigured) as exc:
        send_mail(
            'Subject here',
            'Here is the message.',
            'sender@example.com',
            ['receiver@example.com'],
        )
    assert str(exc.value) == 'You should specify TOKEN to use Postmark email backend'
