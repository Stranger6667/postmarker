import warnings

from .base import Model, ModelManager


class SenderSignature(Model):
    def get(self):
        new_instance = self._manager.get(self.ID)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs):
        response = self._manager.edit(self.ID, **kwargs)
        self._update(response)

    def delete(self):
        return self._manager.delete(self.ID)

    def resend(self):
        return self._manager.resend(self.ID)

    def verifyspf(self):
        return self._manager.verifyspf(self.ID)

    def requestnewdkim(self):
        return self._manager.requestnewdkim(self.ID)


class SenderSignaturesManager(ModelManager):
    name = "senders"
    model = SenderSignature
    token_type = "account"

    def all(self, count=500, offset=0):
        """Gets a list of sender signatures containing brief details associated with your account."""
        responses = self.call_many("GET", "/senders/", count=count, offset=offset)
        return self.expand_responses(responses, "SenderSignatures")

    def get(self, id):
        """Gets all the details for a specific sender signature."""
        response = self.call("GET", "/senders/%s" % id)
        return self._init_instance(response)

    def create(self, FromEmail, Name, ReplyToEmail=None, ReturnPathDomain=None):
        data = {
            "FromEmail": FromEmail,
            "Name": Name,
            "ReplyToEmail": ReplyToEmail,
            "ReturnPathDomain": ReturnPathDomain,
        }
        return self._init_instance(self.call("POST", "/senders/", data=data))

    def edit(self, id, Name, ReplyToEmail=None, ReturnPathDomain=None):
        data = {
            "Name": Name,
            "ReplyToEmail": ReplyToEmail,
            "ReturnPathDomain": ReturnPathDomain,
        }
        return self.call("PUT", "/senders/%s" % id, data=data)

    def delete(self, id):
        return self.call("DELETE", "/senders/%s" % id)["Message"]

    def resend(self, id):
        return self.call("POST", "/senders/%s/resend" % id)["Message"]

    def verifyspf(self, id):
        return self.call("POST", "/senders/%s/verifyspf" % id)

    def requestnewdkim(self, id):
        """Request new DKIM.

        Will query DNS for your domain and attempt to verify the SPF record contains the information for
        Postmark's servers.
        """
        warnings.warn(
            "This method has been deprecated. "
            "Please use the new Domains API (http://developer.postmarkapp.com/developer-api-domains.html) "
            "for updated SPF methods.",
            DeprecationWarning,
        )
        return self.call("POST", "/senders/%s/requestnewdkim" % id)
