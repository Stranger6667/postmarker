# coding: utf-8
from email.mime.base import MIMEBase

import pytest

from postmarker.models.emails import Email


CASSETTE_NAME = 'emails'


ATTACHMENT = {
    'Name': 'readme.txt',
    'Content': 'dGVzdCBjb250ZW50',
    'ContentType': 'text/plain'
}
TUPLE_ATTACHMENT = ATTACHMENT['Name'], ATTACHMENT['Content'], ATTACHMENT['ContentType']
MIME_ATTACHMENT = MIMEBase('text', 'plain')
MIME_ATTACHMENT.set_payload('dGVzdCBjb250ZW50')
MIME_ATTACHMENT.add_header('Content-Disposition', 'attachment', filename='readme.txt')

SUPPORTED_ATTACHMENTS = (ATTACHMENT, MIME_ATTACHMENT, TUPLE_ATTACHMENT)


class TestSimpleSend:

    @pytest.fixture
    def minimal_data(self):
        return {
            'From': 'sender@example.com',
            'To': 'receiver@example.com',
            'Subject': 'Postmark test',
            'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
        }

    def test_default(self, server_client, minimal_data):
        """
        Minimal case.
        """
        response = server_client.emails.send(**minimal_data)
        assert response == {
            'ErrorCode': 0,
            'Message': 'Test job accepted',
            'MessageID': '806aa9ad-689d-48d3-9887-ac0c2bc6f57d',
            'SubmittedAt': '2016-10-06T04:24:31.2196962-04:00',
            'To': 'receiver@example.com'
        }

    @pytest.mark.parametrize('field', ('To', 'Cc', 'Bcc'))
    @pytest.mark.parametrize(
        'value',
        (
            'first@example.com,second@example.com',
            ['first@example.com', 'second@example.com']
        )
    )
    def test_multiple_addresses(self, server_client, minimal_data, patched_request, field, value):
        minimal_data[field] = value
        server_client.emails.send(**minimal_data)
        assert patched_request.call_args[1]['json'][field] == 'first@example.com,second@example.com'

    def test_headers(self, server_client, minimal_data, patched_request):
        minimal_data['Headers'] = {'Test': 1}
        server_client.emails.send(**minimal_data)
        assert patched_request.call_args[1]['json']['Headers'] == [{'Name': 'Test', 'Value': 1}]

    @pytest.mark.parametrize('attachment', SUPPORTED_ATTACHMENTS)
    def test_attachments(self, server_client, minimal_data, patched_request, attachment):
        minimal_data['Attachments'] = [attachment]
        server_client.emails.send(**minimal_data)
        assert patched_request.call_args[1]['json']['Attachments'] == [ATTACHMENT]


class TestModel:

    def test_set_header(self, email):
        assert email.Headers == {}
        email['X-Accept-Language'] = 'en-us, en'
        assert email.Headers == {'X-Accept-Language': 'en-us, en'}
        assert email.as_dict()['Headers'] == [{'Name': 'X-Accept-Language', 'Value': 'en-us, en'}]

    def test_unset_header(self, email):
        email['X-Accept-Language'] = 'en-us, en'
        del email['X-Accept-Language']
        assert email.Headers == {}
        assert email.as_dict()['Headers'] == []

    def test_body(self):
        with pytest.raises(AssertionError) as exc:
            Email(From='sender@example.com', To='receiver@example.com', Subject='Postmark test')
        assert str(exc.value) == 'Provide either email TextBody or HtmlBody or both'

    @pytest.mark.parametrize('attachment', SUPPORTED_ATTACHMENTS)
    def test_attach(self, email, patched_request, attachment):
        email.attach(attachment)
        email.send()
        assert patched_request.call_args[1]['json']['Attachments'] == [ATTACHMENT]

    def test_attach_multiple(self, email, patched_request):
        email.attach(ATTACHMENT, TUPLE_ATTACHMENT, MIME_ATTACHMENT)
        email.send()
        assert patched_request.call_args[1]['json']['Attachments'] == [ATTACHMENT, ATTACHMENT, ATTACHMENT]
