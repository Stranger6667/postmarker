from .base import Model, ModelManager


class MessageStream(Model):
    def __str__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self._data.get("ID"),
        )

    def get(self):
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs):
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def archive(self):
        return self._manager.archive(self.ID)

    def unarchive(self):
        return self._manager.unarchive(self.ID)


class MessageStreamsManager(ModelManager):
    name = "message_streams"
    model = MessageStream

    def get(self, id):
        response = self.call("GET", "/message-streams/%s" % id)
        return self._init_instance(response)

    def create(
        self,
        ID,
        Name,
        MessageStreamType,
        Description=None,
        SubscriptionManagementConfiguration=None,
        UnsubscribeHandlingType=None,
    ):
        """Creates a message stream.

        :param ID: The ID of the message stream being created. This is used when sending messages to specify the sending message stream. For example: "transactional-dev"
        :param Name: Name of message stream
        :param MessageStreamType: The type of message stream being created. Possible options "Broadcasts" or "Transasctional"
        :param Description: Optional. A description of the message stream.
        :param SubscriptionManagementConfiguration: Optional. Subscription management options for the Stream.
        :param UnsubscribeHandlingType: The unsubscribe management option for the stream. For transactional streams default is None. For broadcast streams default is Postmark. Unsubscribe management is required for broadcast message streams, approved accounts can use Custom. Possible options: "none" "Postmark" "Custom".
        :return:
        """
        assert MessageStreamType in (
            "Broadcasts",
            "Transasctional",
        ), "Provide either email TextBody or HtmlBody or both"
        data = {
            "ID": ID,
            "Name": Name,
            "MessageStreamType": MessageStreamType,
            "Description": Description,
            "SubscriptionManagementConfiguration": SubscriptionManagementConfiguration,
            "UnsubscribeHandlingType": UnsubscribeHandlingType,
        }
        return self._init_instance(self.call("POST", "/message-streams", data=data))

    def edit(
        self,
        id,
        Name=None,
        Description=None,
        SubscriptionManagementConfiguration=None,
        UnsubscribeHandlingType=None,
    ):
        data = {}

        if Name is not None:
            data["Name"] = Name

        if Description is not None:
            data["Description"] = Description

        if SubscriptionManagementConfiguration is not None:
            data["SubscriptionManagementConfiguration"] = SubscriptionManagementConfiguration

        if UnsubscribeHandlingType is not None:
            data["UnsubscribeHandlingType"] = UnsubscribeHandlingType

        return self.call("PATCH", "/message-streams/%s" % id, data=data)

    def all(self, MessageStreamType=None, IncludeArchivedStreams=None):
        response = self.call(
            "GET",
            "/message-streams",
            MessageStreamType=MessageStreamType,
            IncludeArchivedStreams=IncludeArchivedStreams,
        )

        return self._init_many(response["MessageStreams"])

    def archive(self, id):
        return self.call("POST", "/message-streams/%s/archive" % id)

    def unarchive(self, id):
        return self.call("PUT", "/message-streams/%s/unarchive" % id)

    def suppressions_dump(
        self,
        stream_id,
        SuppressionReason=None,
        Origin=None,
        todate=None,
        fromdate=None,
        EmailAddress=None,
    ):
        response = self.call(
            "GET",
            "/message-streams/%s/suppressions/dump" % stream_id,
            SuppressionReason=SuppressionReason,
            Origin=Origin,
            todate=todate,
            fromdate=fromdate,
            EmailAddress=EmailAddress,
        )

        return response["Suppressions"]

    def suppressions_create(self, stream_id, *email_addresses):
        data = {"Suppressions": [{"EmailAddress": i} for i in email_addresses]}

        return self.call("POST", "/message-streams/%s/suppressions" % stream_id, data=data)

    def suppressions_delete(self, stream_id, *email_addresses):
        data = {"Suppressions": [{"EmailAddress": i} for i in email_addresses]}

        return self.call("POST", "/message-streams/%s/suppressions/delete" % stream_id, data=data)
