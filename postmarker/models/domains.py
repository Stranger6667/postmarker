# coding: utf-8
from .base import Model, ModelManager


class Domain(Model):

    def __str__(self):
        return '%s: %s (%s)' % (self.__class__.__name__, self._data.get('Name'), self._data.get('ID'))

    def get(self):
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs):
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self):
        return self._manager.delete(self.ID)

    def verifyspf(self):
        return self._manager.verifyspf(self.ID)

    def rotatedkim(self):
        return self._manager.rotatedkim(self.ID)


class DomainsManager(ModelManager):
    name = 'domains'
    model = Domain
    token_type = 'account'

    def get(self, id):
        response = self.call('GET', '/domains/%s' % id)
        return self._init_instance(response)

    def create(self, Name, ReturnPathDomain=None):
        data = {
            'Name': Name,
            'ReturnPathDomain': ReturnPathDomain
        }
        return self._init_instance(self.call('POST', '/domains', data=data))

    def edit(self, id, ReturnPathDomain):
        data = {'ReturnPathDomain': ReturnPathDomain}
        return self.call('PUT', '/domains/%s' % id, data=data)

    def all(self, count=500, offset=0):
        response = self.call('GET', '/domains', count=count, offset=offset)
        return self._init_many(response['Domains'])

    def delete(self, id):
        return self.call('DELETE', '/domains/%s' % id)['Message']

    def verifyspf(self, id):
        return self.call('POST', '/domains/%s/verifyspf' % id)

    def rotatedkim(self, id):
        return self.call('POST', '/domains/%s/rotatedkim' % id)
