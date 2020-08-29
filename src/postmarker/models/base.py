from json import loads

from ..utils import sizes


class Model:
    """Abstract data model for Postmark entities."""

    _data = None

    def __init__(self, manager=None, **kwargs):
        self._manager = manager
        self._update(kwargs)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self._data.get("ID"))

    def __repr__(self):
        return "<%s>" % self

    def _update(self, kwargs):
        if self._data:
            self._data.update(kwargs)
        else:
            self._data = kwargs
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls, json, manager=None):
        data = loads(json)
        return cls(manager=manager, **data)

    def as_dict(self):
        return self._data.copy()


class ModelManager:
    """Proxies calls to main API client. Encapsulates logic of certain part of API - bounces, emails, etc."""

    name = None
    model = None
    token_type = "server"
    count_key = "count"
    offset_key = "offset"
    max_chunk_size = 500

    def __init__(self, client):
        self.client = client

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<%s>" % self

    def _init_instance(self, data):
        return self.model(manager=self, **data)  # pylint: disable=not-callable

    def _init_many(self, data):
        return [self._init_instance(part) for part in data]

    def call(self, *args, **kwargs):
        kwargs["token_type"] = self.token_type
        return self.client.call(*args, **kwargs)

    def call_many(self, *args, **kwargs):
        return list(self._call_many(*args, **kwargs))

    def _call_many(self, *args, **kwargs):
        count = kwargs.pop(self.count_key)
        offset = kwargs.pop(self.offset_key)
        loaded_items_count = 0
        for _count, _offset in sizes(count, offset, self.max_chunk_size):
            response = self.call(*args, **self.update_kwargs(kwargs, _count, _offset))
            loaded_items_count += _count
            yield response
            # We expect, that we will load `TotalCount` - offset items.
            # This number will be less or equal to number of already loaded items.
            # It could be less in case if latest response contains less items than provided `count` value.
            if response["TotalCount"] - offset <= loaded_items_count:
                break

    def expand_responses(self, responses, key):
        items = [self._init_many(response[key]) for response in responses]
        return sum(items, [])

    def update_kwargs(self, kwargs, count, offset):
        """Helper to support handy dictionaries merging on all Python versions."""
        kwargs.update({self.count_key: count, self.offset_key: offset})
        return kwargs


class SubModelManager(ModelManager):
    """Works with multiple model managers.

    Example:
        >>> postmark = PostmarkClient(server_token='TEST')
        >>> postmark.messages.outbound.all()
        []

    """

    _managers = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_managers()

    def _setup_managers(self):
        for manager_class in self._managers:
            instance = manager_class(self.client)
            setattr(self, instance.name, instance)


class MessageModel(Model):
    @property
    def message(self):
        return self._manager.client.messages.outbound.get(self.MessageID)
