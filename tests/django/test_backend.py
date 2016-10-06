# coding: utf-8
import pytest
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
