# coding: utf-8
import pytest

from postmarker.webhooks import DeliveryWebhook, InboundWebhook, OpenWebhook


OPEN_WEBHOOK = '''{
  "FirstOpen": true,
  "Client": {
    "Name": "Chrome 35.0.1916.153",
    "Company": "Google",
    "Family": "Chrome"
  },
  "OS": {
    "Name": "OS X 10.7 Lion",
    "Company": "Apple Computer, Inc.",
    "Family": "OS X 10"
  },
  "Platform": "WebMail",
  "UserAgent": "Some UA string",
  "ReadSeconds": 5,
  "Geo": {
    "CountryISOCode": "RS",
    "Country": "Serbia",
    "RegionISOCode": "VO",
    "Region": "Autonomna Pokrajina Vojvodina",
    "City": "Novi Sad",
    "Zip": "21000",
    "Coords": "45.2517,19.8369",
    "IP": "188.2.95.4"
  },
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "ReceivedAt": "2014-06-01T12:00:00",
  "Tag": "welcome-email",
  "Recipient": "john@example.com"
}'''


@pytest.fixture
def open_webhook():
    return OpenWebhook(OPEN_WEBHOOK)


DELIVERY_WEBHOOK = '''{
  "ServerId": 23,
  "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
  "Recipient": "john@example.com",
  "Tag": "welcome-email",
  "DeliveredAt": "2014-08-01T13:28:10.2735393-04:00",
  "Details": "Test delivery webhook details"
}'''


@pytest.fixture
def delivery_webhook():
    return DeliveryWebhook(DELIVERY_WEBHOOK)


INBOUND_WEBHOOK = '''{
"BccFull": [
  {"MailboxHash": "", "Name": "First Bcc", "Email": "firstbcc@postmarkapp.com"},
  {"MailboxHash": "", "Name": "", "Email": "secondbcc@postmarkapp.com"}
],
"Tag": "TestTag",
"StrippedTextReply": "This is the reply text",
"FromFull": {"MailboxHash": "", "Name": "Postmarkapp Support", "Email": "support@postmarkapp.com"},
"CcFull": [
  {"MailboxHash": "", "Name": "First Cc", "Email": "firstcc@postmarkapp.com"},
  {"MailboxHash": "", "Name": "", "Email": "secondCc@postmarkapp.com"}
],
"Cc": "\\"First Cc\\" <firstcc@postmarkapp.com>, secondCc@postmarkapp.com>",
"To": "\\"Firstname Lastname\\" <yourhash+SampleHash@inbound.postmarkapp.com>",
"Attachments": [
  {
    "ContentType": "text/plain",
    "Name": "test.txt",
    "ContentLength": 45,
    "Content": "VGhpcyBpcyBhdHRhY2htZW50IGNvbnRlbnRzLCBiYXNlLTY0IGVuY29kZWQu"
  }
],
"From": "support@postmarkapp.com",
"FromName": "Postmarkapp Support",
"Date": "Fri, 1 Aug 2014 16:45:32 -04:00",
"MessageID": "73e6d360-66eb-11e1-8e72-a8904824019b",
"TextBody": "This is a test text body.",
"ToFull": [
  {"MailboxHash": "SampleHash", "Name": "Firstname Lastname", "Email": "yourhash+SampleHash@inbound.postmarkapp.com"}
],
"HtmlBody": "<html><body><p>This is a test html body.<\\\\/p><\\\\/body><\\\\/html>",
"MailboxHash": "SampleHash",
"Headers": [
  {"Name": "X-Header-Test", "Value": ""},
  {"Name": "X-Spam-Status", "Value": "No"},
  {"Name": "X-Spam-Score", "Value": "-0.1"},
  {"Name": "X-Spam-Tests", "Value": "DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,SPF_PASS"}
],
"ReplyTo": "replyto@postmarkapp.com",
"Subject": "Test subject",
"OriginalRecipient": "yourhash+SampleHash@inbound.postmarkapp.com",
"Bcc": "\\"First Bcc\\" <firstbcc@postmarkapp.com>, secondbcc@postmarkapp.com>"
}'''


@pytest.fixture
def inbound_webhook():
    return InboundWebhook(INBOUND_WEBHOOK)


@pytest.fixture
def attachment(inbound_webhook):
    return inbound_webhook.Attachments[0]
