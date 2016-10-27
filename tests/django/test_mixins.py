# coding: utf-8
import pytest
from django import VERSION
from django.core.mail import EmailMultiAlternatives

from postmarker.django import PostmarkEmailMixin


pytestmark = pytest.mark.usefixtures('outbox')


class TaggedEmail(PostmarkEmailMixin, EmailMultiAlternatives):
    pass


@pytest.mark.skipif(VERSION[:2] < (1, 8), reason='Context manager protocol was added in Django 1.8')
def test_tags(patched_request):
    TaggedEmail(
        'Subject', 'Body', 'sender@example.com', ['receiver@example.com'],
        tag='Test tag'
    ).send()
    assert patched_request.call_args[1]['json'][0] == {
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
        'Tag': 'Test tag',
        'From': 'sender@example.com'
    }