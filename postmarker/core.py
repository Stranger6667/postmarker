# coding: utf-8
import requests

from ._compat import urljoin


class BaseClient(object):
    """
    Basic class for API clients. Provides basic functionality to make requests.
    """
    root_url = 'https://api.postmarkapp.com/'
    auth_header_name = None

    def __init__(self, token=None):
        assert token, 'You have to provide token to use Postmark API'
        self.token = token

    def _call(self, method, endpoint):
        """
        Low-level call to Postmark API.
        """
        headers = {
            self.auth_header_name: self.token,
            'Accept': 'application/json',
        }
        url = urljoin(self.root_url, endpoint)
        return requests.request(method, url, headers=headers)


class ServerClient(BaseClient):
    """
    Provides an interface for actions, that require server level privileges.
    """
    auth_header_name = 'X-Postmark-Server-Token'


class AccountClient(BaseClient):
    """
    Provides an interface for actions, that require account level privileges.
    """
    auth_header_name = 'X-Postmark-Account-Token'
