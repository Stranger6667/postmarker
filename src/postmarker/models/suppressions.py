"""Supressions

Information on suppression lists"""

from .base import ModelManager, MessageModel


class Suppression(MessageModel):
    """Suppression model."""
    email_address = None
    suppression_reason = None
    origin = None
    created_at = None

    def __init__(self, email_address=None, suppression_reason=None, origin=None, created_at=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email_address = email_address
        self.suppression_reason = suppression_reason
        self.origin = origin
        self.created_at = created_at


class SuppressionResponse(MessageModel):
    """Suppression request model."""
    email_address = None
    status = None
    message = None

    def __init__(self, email_address=None, status=None, message=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email_address = email_address
        self.status = status
        self.message = message


class SuppressionManager(ModelManager):
    name = "suppressions"
    model = Suppression

    def _manage_suppression(self, endpoint, emails):
        if type(emails) != list:
            emails = [emails]
        data = {'Suppressions': [{'EmailAddress': email} for email in emails]}
        response = self.call("POST", endpoint=endpoint, data=data)
        suppression_response_list = []
        for suppression in response['Suppressions']:
            suppression_response_list.append(SuppressionResponse(
                email_address=suppression['EmailAddress'],
                status=suppression['Status'],
                message=suppression['Message']
            ))
        return suppression_response_list

    def get_suppression(self, stream_id, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if key in ['EmailAddress', 'SuppressionReason', 'Origin', 'todate', 'fromdate']:
                params[key] = value
            else:
                raise ValueError(f"Invalid parameter: {key}")
        endpoint = f"/message-streams/{stream_id}/suppressions"
        response = self.call("GET", endpoint=endpoint, params=params)
        suppression_list = []
        for suppression in response['Suppressions']:
            suppression_list.append(Suppression(
                email_address=suppression['EmailAddress'],
                suppression_reason=suppression['SuppressionReason'],
                origin=suppression['Origin'],
                created_at=suppression['CreatedAt']
            ))
        return suppression_list

    def add(self, stream_id, emails):
        endpoint = f"/message-streams/{stream_id}/suppressions"
        return self._manage_suppression(endpoint, emails)

    def delete(self, stream_id, emails):
        endpoint = f"/message-streams/{stream_id}/suppressions/delete"
        return self._manage_suppression(endpoint, emails)
