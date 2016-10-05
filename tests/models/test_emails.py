# coding: utf-8


CASSETTE_NAME = 'emails'


def test_send_email(server_client):
    response = server_client.emails.send(
        From='sender@example.com',
        To='receiver@example.com',
        Subject='Postmark test',
        HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
    )
    assert response == {
        'ErrorCode': 0,
        'Message': 'Test job accepted',
        'MessageID': '61660122-c7fd-48e5-a7eb-97e82f704bd9',
        'SubmittedAt': '2016-10-05T07:48:24.2900162-04:00',
        'To': 'receiver@example.com'
    }
