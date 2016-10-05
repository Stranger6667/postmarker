# coding: utf-8


class Model(object):
    """
    Abstract data model for Postmark entities.
    """

    def __init__(self, manager=None, **kwargs):
        self._manager = manager
        self._data = kwargs
        self._update(kwargs)

    def _update(self, kwargs):
        self.__dict__.update(kwargs)

    def as_dict(self):
        return self._data.copy()


class ModelManager(object):
    """
    Proxies calls to main API client. Encapsulates logic of certain part of API - bounces, emails, etc.
    """
    name = None
    model = None

    def __init__(self, client):
        self.client = client

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % self

    __unicode__ = __str__

    def _init_instance(self, data):
        return self.model(manager=self, **data)

    def _call(self, *args, **kwargs):
        return self.client._call(*args, **kwargs)
