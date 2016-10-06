# coding: utf-8
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

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


def get_mime_message(text, **kwargs):
    instance = MIMEText(text)
    for key, value in kwargs.items():
        instance[key] = value
    return instance

MIME_MESSAGE = get_mime_message(
    'Text',
    **{
        'From': 'sender@example.com',
        'To': 'receiver@example.com',
        'Subject': 'Test subject',
        'Cc': 'cc@example.com',
        'Bcc': 'bcc@example.com',
        'Reply-To': 'replyto@example.com',
    }
)


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

    def test_mime_text(self, server_client):
        response = server_client.emails.send(message=MIME_MESSAGE)
        assert response == {
            'ErrorCode': 0,
            'Message': 'Test job accepted',
            'MessageID': '96a981da-9b7c-4aa9-bda2-84ab99097686',
            'SubmittedAt': '2016-10-06T10:05:30.570118-04:00',
            'To': 'receiver@example.com'
        }

    def test_incomplete_mime(self, server_client):
        message = get_mime_message('Text', From='sender@example.com', To='receiver@example.com')
        response = server_client.emails.send(message=message)
        assert response == {
            'ErrorCode': 0,
            'Message': 'Test job accepted',
            'MessageID': '03285bf8-2a7d-4c42-9e15-b51062e2bc9a',
            'SubmittedAt': '2016-10-06T10:26:27.8804172-04:00',
            'To': 'receiver@example.com'
        }

    def test_invalid(self, server_client):
        with pytest.raises(TypeError) as exc:
            server_client.emails.send(message=object())
        assert str(exc.value) == 'message should be either Email or MIMEText instance'

    def test_message_and_kwargs(self, server_client, email):
        with pytest.raises(AssertionError) as exc:
            server_client.emails.send(message=email, From='test@test.com')
        assert str(exc.value) == 'You should specify either message or From and To parameters'

    def test_send_email(self, server_client, email, patched_request):
        server_client.emails.send(message=email)
        assert patched_request.call_args[1]['json'] == email.as_dict()

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


class TestBatchSend:

    def test_email_instance(self, server_client, email, patched_request):
        server_client.emails.send_batch(email)
        assert patched_request.call_args[1]['json'] == (email.as_dict(), )

    def test_dict(self, server_client, email, patched_request):
        email_dict = {
            'From': email.From,
            'To': email.To,
            'TextBody': email.TextBody
        }
        expected = {
            'From': email.From,
            'To': email.To,
            'TextBody': email.TextBody,
            'Headers': [],
            'Attachments': [],
        }
        server_client.emails.send_batch(email_dict)
        assert patched_request.call_args[1]['json'] == (expected, )

    def test_multiple(self, server_client, email, patched_request):
        server_client.emails.send_batch(email, email)
        assert patched_request.call_args[1]['json'] == (email.as_dict(), email.as_dict())

    def test_mime(self, server_client, patched_request):
        server_client.emails.send_batch(MIME_MESSAGE)
        email = Email.from_mime(MIME_MESSAGE, server_client)
        assert patched_request.call_args[1]['json'] == (email.as_dict(), )

    def test_invalid(self, server_client):
        with pytest.raises(ValueError):
            server_client.emails.send_batch(object())


class TestEmailBatch:

    def test_len(self, email_batch):
        assert len(email_batch) == 1


class TestEmail:

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

    def test_from_mime(self, server_client):
        email = Email.from_mime(MIME_MESSAGE, server_client)
        assert email.TextBody == 'Text'
        assert email.From == MIME_MESSAGE['From']
        assert email.To == MIME_MESSAGE['To']
        assert email.Subject == MIME_MESSAGE['Subject']
        assert email.Cc == MIME_MESSAGE['Cc']
        assert email.Bcc == MIME_MESSAGE['Bcc']
        assert email.ReplyTo == MIME_MESSAGE['Reply-To']
