# coding: utf-8
import requests

from ._compat import urljoin
from .models.bounces import BounceManager


class BaseClient(object):
    """
    Basic class for API clients. Provides basic functionality to make requests.
    """
    root_url = 'https://api.postmarkapp.com/'
    auth_header_name = None
    _managers = ()

    def __init__(self, token=None):
        assert token, 'You have to provide token to use Postmark API'
        self.token = token
        self._setup_managers()

    def _setup_managers(self):
        """
        Allows to access manager by model name.

        >>> client = ServerClient(token='TEST')
        >>> client.bounces
        <BounceManager>
        """
        for manager_class in self._managers:
            instance = manager_class(self)
            setattr(self, instance.name, instance)

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = requests.Session()
        return self._session

    def _call(self, method, endpoint, data=None, **kwargs):
        """
        Low-level call to Postmark API.
        """
        headers = {
            self.auth_header_name: self.token,
            'Accept': 'application/json',
        }
        if method != 'GET':
            headers['Content-Type'] = 'application/json'
        url = urljoin(self.root_url, endpoint)
        return self.session.request(method, url, data=data, params=kwargs, headers=headers)


class ServerClient(BaseClient):
    """
    Provides an interface for actions, that require server level privileges.
    """
    auth_header_name = 'X-Postmark-Server-Token'
    _managers = (
        BounceManager,
    )


class AccountClient(BaseClient):
    """
    Provides an interface for actions, that require account level privileges.
    """
    auth_header_name = 'X-Postmark-Account-Token'
