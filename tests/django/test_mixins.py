# coding: utf-8
import pytest
from django.core.mail import EmailMultiAlternatives

from postmarker.django import PostmarkEmailMixin


pytestmark = pytest.mark.usefixtures('outbox')


class TaggedEmail(PostmarkEmailMixin, EmailMultiAlternatives):
    pass


def test_tags(postmark_request):
    TaggedEmail(
        'Subject', 'Body', 'sender@example.com', ['receiver@example.com'],
        tag='Test tag'
    ).send()
    assert postmark_request.call_args[1]['json'][0] == {
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
