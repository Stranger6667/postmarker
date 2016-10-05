# coding: utf-8
import requests

from ._compat import urljoin, with_metaclass
from .exceptions import ConfigError
from .models.bounces import BounceManager


class ClientMeta(type):

    def __new__(mcs, name, bases, members):
        new_class = super(ClientMeta, mcs).__new__(mcs, name, bases, members)
        mcs.check_managers(new_class)
        return new_class

    @staticmethod
    def check_managers(new_class):
        """
        `_managers` attribute should not contains:

         - Managers with same names
         - Managers with names that clashes with client's attributes
        """
        managers_names = [manager.name for manager in new_class._managers]
        if len(managers_names) != len(set(managers_names)):
            raise ConfigError('Defined managers names are not unique')
        if any(hasattr(new_class, manager_name) for manager_name in managers_names):
            raise ConfigError('Defined managers names override client\'s members')


class BaseClient(with_metaclass(ClientMeta)):
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

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.token)

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
        url = urljoin(self.root_url, endpoint)
        return self.session.request(method, url, json=data, params=kwargs, headers=headers)


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
