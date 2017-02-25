# coding: utf-8
from .._compat import with_metaclass
from ..utils import ManageableMeta


class Model(object):
    """
    Abstract data model for Postmark entities.
    """
    _data = None

    def __init__(self, manager=None, **kwargs):
        self._manager = manager
        self._update(kwargs)

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self._data.get('ID'))

    def __repr__(self):
        return '<%s>' % self

    def __unicode__(self):
        return self.__str__()

    def _update(self, kwargs):
        if self._data:
            self._data.update(kwargs)
        else:
            self._data = kwargs
        self.__dict__.update(kwargs)

    def as_dict(self):
        return self._data.copy()


class ModelManager(object):
    """
    Proxies calls to main API client. Encapsulates logic of certain part of API - bounces, emails, etc.
    """
    name = None
    model = None
    token_type = 'server'

    def __init__(self, client):
        self.client = client

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % self

    __unicode__ = __str__

    def _init_instance(self, data):
        return self.model(manager=self, **data)

    def _init_many(self, data):
        return [self._init_instance(part) for part in data]

    def call(self, *args, **kwargs):
        kwargs['token_type'] = self.token_type
        return self.client.call(*args, **kwargs)


class SubModelManager(with_metaclass(ManageableMeta, ModelManager)):
    """
    Works with multiple model managers. Example:

    >>> postmark = PostmarkClient(token='TEST')
    >>> postmark.messages.outbound.all()
    []
    """
    _managers = ()

    def __init__(self, *args, **kwargs):
        super(SubModelManager, self).__init__(*args, **kwargs)
        self._setup_managers()

    def _setup_managers(self):
        for manager_class in self._managers:
            instance = manager_class(self.client)
            setattr(self, instance.name, instance)
