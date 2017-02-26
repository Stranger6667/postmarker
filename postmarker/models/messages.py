# coding: utf-8
from .base import Model, ModelManager, SubModelManager


class Open(Model):

    def __str__(self):
        return 'Open from %s' % self._data.get('Recipient')


class OpensManager(ModelManager):
    name = 'opens'
    model = Open

    def all(self, count=500, offset=0, recipient=None, tag=None, client_name=None, client_company=None,
            client_family=None, os_name=None, os_family=None, os_company=None, platform=None, country=None, region=None,
            city=None):
        response = self.call(
            'GET', '/messages/outbound/opens', count=count, offset=offset, recipient=recipient, tag=tag,
            client_name=client_name, client_company=client_company, client_family=client_family, os_name=os_name,
            os_family=os_family, os_company=os_company, platform=platform, country=country, region=region, city=city
        )
        return self._init_many(response['Opens'])

    def get(self, id, count=500, offset=0):
        return self.call('GET', '/messages/outbound/opens/%s' % id, count=count, offset=offset)


class BaseMessage(Model):

    def get_details(self):
        return self._manager.get_details(self.MessageID)


class OutboundMessage(BaseMessage):

    def __str__(self):
        recipients = ', '.join(self._data.get('Recipients'))
        return '%s message to %s' % (self._data.get('Status'), recipients)

    def get_dump(self):
        return self._manager.get_dump(self.MessageID)

    def opens(self, count=500, offset=0):
        return self._manager.opens.get(self.MessageID, count=count, offset=offset)


class OutboundMessageManager(SubModelManager):
    name = 'outbound'
    model = OutboundMessage
    _managers = (
        OpensManager,
    )

    def all(self, count=500, offset=0, recipient=None, fromemail=None, tag=None, status=None, todate=None,
            fromdate=None):
        """
        Lets you get all the details about any outbound or inbound message that you sent or received
        through a specific server. Messages expire after 45 days.

        :param int count: Number of messages to return per request. Max 500.
        :param int offset: Number of messages to skip.
        :param str recipient: Filter by the user who was receiving the email.
        :param str fromemail: Filter by the sender email address.
        :param str tag: Filter by tag.
        :param str status: Filter by status (queued or sent).
        :param date todate: Filter messages up to the date specified (inclusive).
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :return: A list of :py:class:`OutboundMessage` instances.
        :rtype: `list`
        """
        response = self.call(
            'GET', '/messages/outbound', count=count, offset=offset, recipient=recipient, fromemail=fromemail, tag=tag,
            status=status, todate=todate, fromdate=fromdate,
        )
        return self._init_many(response['Messages'])

    def get_details(self, id):
        return self.call('GET', '/messages/outbound/%s/details' % id)

    def get_dump(self, id):
        return self.call('GET', '/messages/outbound/%s/dump' % id).get('Body')


class InboundMessage(BaseMessage):

    def __str__(self):
        return '%s message from %s' % (self._data.get('Status'), self._data.get('From'))

    def bypass(self):
        return self._manager.bypass(self.MessageID)

    def retry(self):
        return self._manager.retry(self.MessageID)


class InboundMessageManager(ModelManager):
    name = 'inbound'
    model = InboundMessage

    def all(self, count=500, offset=0, recipient=None, fromemail=None, tag=None, subject=None, mailboxhash=None,
            status=None, todate=None, fromdate=None):
        """

        :param count: Number of messages to return per request. Max 500.
        :param offset: Number of messages to skip.
        :param recipient: Filter by the user who was receiving the email.
        :param fromemail: Filter by the sender email address.
        :param tag: Filter by tag.
        :param subject: Filter by email subject.
        :param mailboxhash: Filter by mailboxhash.
        :param status: Filter by status (blocked, processed, queued, failed, scheduled).
        :param date todate: Filter messages up to the date specified (inclusive).
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :return: A list of :py:class:`InboundMessage` instances.
        :rtype: `list`
        """
        response = self.call(
            'GET', '/messages/inbound', count=count, offset=offset, recipient=recipient, fromemail=fromemail, tag=tag,
            subject=subject, mailboxhash=mailboxhash, status=status, todate=todate, fromdate=fromdate,
        )
        return self._init_many(response['InboundMessages'])

    def get_details(self, id):
        return self.call('GET', '/messages/inbound/%s/details' % id)

    def bypass(self, id):
        return self.call('PUT', '/messages/inbound/%s/bypass' % id)

    def retry(self, id):
        return self.call('PUT', '/messages/inbound/%s/retry' % id)


class MessageManager(SubModelManager):
    name = 'messages'
    _managers = (
        OutboundMessageManager,
        InboundMessageManager,
    )
