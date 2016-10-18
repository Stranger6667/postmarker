# coding: utf-8
from .base import Model, ModelManager


class Server(Model):

    def __str__(self):
        return '%s: %s (%s)' % (self.__class__.__name__, self.Name, self._data.get('ID'))

    def edit(self, **kwargs):
        response = self._manager.edit(**kwargs)
        self._update(response)


class ServerManager(ModelManager):
    """
    Lets you get or edit details of the specific server.
    """
    name = 'server'
    model = Server

    def get(self):
        response = self.call('GET', '/server')
        return self._init_instance(response)

    def edit(self, **kwargs):
        return self.call('PUT', '/server', data=kwargs)
