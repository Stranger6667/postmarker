# coding: utf-8
from .base import Model, ModelManager


class Bounce(Model):

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self._data.get('ID'))

    def __repr__(self):
        return '<%s>' % self

    __unicode__ = __str__

    @property
    def dump(self):
        return self._manager.get_dump(self.ID)

    def activate(self):
        response = self._manager.activate(self.ID)
        self._update(response['Bounce'])
        return response['Message']


class BounceManager(ModelManager):
    name = 'bounces'
    model = Bounce

    @property
    def deliverystats(self):
        return self._call('GET', '/deliverystats').json()

    @property
    def tags(self):
        return self._call('GET', '/bounces/tags').json()

    def get(self, id):
        response = self._call('GET', '/bounces/%s' % id)
        return self._init_instance(response.json())

    def all(self, count=500, offset=0):
        response = self._call('GET', '/bounces/', count=count, offset=offset)
        return [self._init_instance(bounce) for bounce in response.json()['Bounces']]

    def activate(self, id):
        return self._call('PUT', '/bounces/%s/activate' % id).json()

    def get_dump(self, id):
        return self._call('GET', '/bounces/%s/dump' % id).json()
