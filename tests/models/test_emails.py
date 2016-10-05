# coding: utf-8
import pytest

from postmarker.models.emails import Email

CASSETTE_NAME = 'emails'


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
            'MessageID': '4b982f10-40bf-4a62-ade4-696bf0eaeb3a',
            'SubmittedAt': '2016-10-05T09:00:05.900306-04:00',
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


class TestModel:

    def test_set_header(self, email):
        assert email.Headers == {}
        email['X-Accept-Language'] = 'en-us, en'
        assert email.Headers == {'X-Accept-Language': 'en-us, en'}
        assert email.as_dict()['Headers'] == [{'Name': 'X-Accept-Language', 'Value': 'en-us, en'}]

    def test_body(self):
        with pytest.raises(AssertionError) as exc:
            Email(From='sender@example.com', To='receiver@example.com', Subject='Postmark test')
        assert str(exc.value) == 'Provide either email TextBody or HtmlBody or both'

    def test_raw_attachment(self, email, patched_request):
        attachments = [{'Name': 'readme.txt', 'Content': 'dGVzdCBjb250ZW50', 'ContentType': 'text/plain'}]
        email._data['Attachments'] = attachments
        email.send()
        assert patched_request.call_args[1]['json']['Attachments'] == attachments
