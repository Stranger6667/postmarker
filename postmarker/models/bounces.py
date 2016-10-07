# coding: utf-8
"""
Information about bounces is available via :py:class:`~postmarker.models.bounces.BounceManager`,
which is an attribute of ``server_client`` instance.
"""
from .base import Model, ModelManager


class Bounce(Model):
    """
    Bounce model.
    """

    @property
    def dump(self):
        """
        Gets SMTP data dump.

        :return: Dump of SMTP data if it is available.
        :rtype: `str` or `None`
        """
        return self._manager.get_dump(self.ID)

    def activate(self):
        """
        Activates the bounce instance and updates it with latest data.

        :return: Activation status.
        :rtype: `str`
        """
        response = self._manager.activate(self.ID)
        self._update(response['Bounce'])
        return response['Message']


class BounceManager(ModelManager):
    """
    Encapsulates logic about bounces.
    """
    name = 'bounces'
    model = Bounce

    @property
    def deliverystats(self):
        """
        Returns number of inactive emails and list of bounce types with total counts.

        :rtype: `dict`
        """
        return self._call('GET', '/deliverystats').json()

    @property
    def tags(self):
        """
        A list of tags that have generated bounces for a given server.

        :rtype: `list`
        """
        return self._call('GET', '/bounces/tags').json()

    def get(self, id):
        """
        Returns a single bounce.

        :param int id: Bounce ID.
        :rtype: :py:class:`Bounce`
        """
        response = self._call('GET', '/bounces/%s' % id)
        return self._init_instance(response.json())

    def all(self, count=500, offset=0, type=None, inactive=None, emailFilter=None, tag=None, messageID=None,
            fromdate=None, todate=None):
        """
        Returns many bounces.

        :param int count: Number of bounces to return per request. Max 500.
        :param int offset: Number of bounces to skip.
        :param str type: Filter by type of bounce.
        :param bool inactive: Filter by emails that were deactivated by Postmark due to the bounce.
        :param str emailFilter: Filter by email address.
        :param str tag: Filter by tag.
        :param str messageID: Filter by messageID.
        :param date fromdate: Filter messages starting from the date specified (inclusive).
        :param date todate: Filter messages up to the date specified (inclusive).
        :return: A list of :py:class:`Bounce` instances.
        :rtype: `list`
        """
        response = self._call(
            'GET', '/bounces/', count=count, offset=offset, type=type, inactive=inactive, emailFilter=emailFilter,
            tag=tag, messageID=messageID, fromdate=fromdate, todate=todate
        )
        return [self._init_instance(bounce) for bounce in response.json()['Bounces']]

    def activate(self, id):
        """
        Activates a bounce.

        :param int id: Bounce ID.
        :return: Activation result and bounce data.
        :rtype: `dict`
        """
        return self._call('PUT', '/bounces/%s/activate' % id).json()

    def get_dump(self, id):
        """
        Gets SMTP data dump.

        :param int id: Bounce ID.
        :return: Dump of SMTP data if it is available.
        :rtype: `str` or `None`
        """
        dump = self._call('GET', '/bounces/%s/dump' % id).json()
        return dump.get('Body')
