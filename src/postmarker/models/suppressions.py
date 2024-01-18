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
