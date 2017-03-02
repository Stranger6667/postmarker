# coding: utf-8
from base64 import b64decode
from email.mime.base import MIMEBase
from json import loads
from os.path import join


class InboundWebhook(object):

    def __init__(self, data=None, json=None):
        assert not (data and json), 'You could pass only `data` or `json`, not both'
        if json is not None:
            self._data = json
        else:
            self._data = loads(data)

    def __getitem__(self, item):
        for header in self._data['Headers']:
            if header['Name'] == item:
                return header['Value']
        raise KeyError

    @property
    def Attachments(self):
        attachments = self._data.get('Attachments', ())
        return [Attachment(data) for data in attachments]

    @property
    def Bcc(self):
        return self._data.get('Bcc')

    @property
    def BccFull(self):
        return self._data.get('BccFull')

    @property
    def Cc(self):
        return self._data.get('Cc')

    @property
    def CcFull(self):
        return self._data.get('CcFull')

    @property
    def Date(self):
        return self._data.get('Date')

    @property
    def From(self):
        return self._data.get('From')

    @property
    def FromFull(self):
        return self._data.get('FromFull')

    @property
    def FromName(self):
        return self._data.get('FromName')

    @property
    def Headers(self):
        return self._data.get('Headers')

    @property
    def HtmlBody(self):
        return self._data.get('HtmlBody')

    @property
    def MailboxHash(self):
        return self._data.get('MailboxHash')

    @property
    def MessageID(self):
        return self._data.get('MessageID')

    @property
    def OriginalRecipient(self):
        return self._data.get('OriginalRecipient')

    @property
    def ReplyTo(self):
        return self._data.get('ReplyTo')

    @property
    def StrippedTextReply(self):
        return self._data.get('StrippedTextReply')

    @property
    def Subject(self):
        return self._data.get('Subject')

    @property
    def Tag(self):
        return self._data.get('Tag')

    @property
    def TextBody(self):
        return self._data.get('TextBody')

    @property
    def To(self):
        return self._data.get('To')

    @property
    def ToFull(self):
        return self._data.get('ToFull')


class Attachment(object):

    def __init__(self, data):
        self._data = data

    def __str__(self):
        return self._data['Name']

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __len__(self):
        return self._data['ContentLength']

    @property
    def Name(self):
        return self._data['Name']

    @property
    def ContentType(self):
        return self._data['ContentType']

    @property
    def ContentLength(self):
        return self._data['ContentLength']

    @property
    def Content(self):
        return self._data['Content']

    @property
    def decoded(self):
        return b64decode(self.Content.encode('ascii'))

    def save(self, directory):
        filename = join(directory, self.Name)
        with open(filename, 'wb') as fd:
            fd.write(self.decoded)
        return filename

    def as_mime(self):
        maintype, subtype = self.ContentType.split('/')
        message = MIMEBase(maintype, subtype)
        message.set_payload(self.Content)
        message['Content-Transfer-Encoding'] = 'base64'
        message.add_header('Content-Disposition', 'attachment', filename=self.Name)
        return message
