from .base import Model, ModelManager


class Incident(Model):
    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self._data.get("id"))


class IncidentsManager(ModelManager):
    name = "incidents"
    model = Incident

    def call(self, *args, **kwargs):
        return self.client.call_status(*args, **kwargs)

    @property
    def last(self):
        return self._init_instance(self.call("last_incident"))

    def all(self):
        return self._init_many(self.call("incidents"))

    def get(self, id):
        return self._init_instance(self.call("incidents/%s" % id))


class StatusManager(ModelManager):
    """Gathers logic about Postmark systems status."""

    name = "status"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.incidents = IncidentsManager(self.client)

    def call(self, *args, **kwargs):
        return self.client.call_status(*args, **kwargs)

    def get(self):
        return self.call("status")

    @property
    def services(self):
        return self.call("services")

    @property
    def availability(self):
        return self.call("services/availability")

    @property
    def delivery(self):
        return self.call("delivery")
