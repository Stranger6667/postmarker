# coding: utf-8
from .base import Model, ModelManager


class Incident(Model):

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self._data.get('id'))


class IncidentsManager(ModelManager):
    name = 'incidents'
    model = Incident

    def call(self, *args, **kwargs):
        return self.client.call_status(*args, **kwargs)

    @property
    def last(self):
        return self._init_instance(self.call('last_incident').json())

    def all(self):
        return [self._init_instance(incident) for incident in self.call('incidents').json()]

    def get(self, id):
        return self._init_instance(self.call('incidents/%s' % id).json())


class StatusManager(ModelManager):
    """
    Gathers logic about Postmark systems status.
    """
    name = 'status'

    def __init__(self, *args, **kwargs):
        super(StatusManager, self).__init__(*args, **kwargs)
        self.incidents = IncidentsManager(self.client)

    def call(self, *args, **kwargs):
        return self.client.call_status(*args, **kwargs)

    def get(self):
        return self.call('status').json()

    @property
    def services(self):
        return self.call('services').json()

    @property
    def availability(self):
        return self.call('services/availability').json()

    @property
    def delivery(self):
        return self.call('delivery').json()
