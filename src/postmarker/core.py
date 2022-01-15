import sys
from urllib.parse import urljoin

import requests

from . import __version__
from .exceptions import ClientError, SpamAssassinError
from .logging import get_logger
from .models.bounces import BounceManager
from .models.domains import DomainsManager
from .models.emails import EmailManager
from .models.messages import MessageManager
from .models.senders import SenderSignaturesManager
from .models.server import ServerManager
from .models.stats import StatsManager
from .models.status import StatusManager
from .models.templates import TemplateManager
from .models.triggers import TriggersManager
from .utils import get_args

DEFAULT_API = "https://api.postmarkapp.com/"
STATUS_API = "https://status.postmarkapp.com/api/1.0/"
SPAMCHECK_API = "http://spamcheck.postmarkapp.com/filter/"
USER_AGENT = "Postmarker/%s" % __version__
TEST_TOKEN = "POSTMARK_API_TEST"


class PostmarkClient:
    """Basic class for API clients. Provides basic functionality to make requests."""

    _managers = (
        BounceManager,
        DomainsManager,
        EmailManager,
        MessageManager,
        SenderSignaturesManager,
        ServerManager,
        StatsManager,
        StatusManager,
        TemplateManager,
        TriggersManager,
    )

    def __init__(
        self,
        server_token=None,
        account_token=None,
        verbosity=0,
        max_retries=0,
        timeout=None,
        logs_stream=sys.stdout,
        root_api_url=DEFAULT_API,
    ):
        assert server_token, "You have to provide token to use Postmark API"
        self.server_token = server_token
        self.account_token = account_token
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = get_logger("Postmarker", verbosity, logs_stream)
        self.root_api_url = root_api_url
        self._setup_managers()

    @classmethod
    def from_config(cls, config, prefix="postmark_", is_uppercase=False):
        """Helper method for instantiating PostmarkClient from dict-like objects."""
        kwargs = {}
        for arg in get_args(cls):
            key = prefix + arg
            if is_uppercase:
                key = key.upper()
            else:
                key = key.lower()
            if key in config:
                kwargs[arg] = config[key]
        return cls(**kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.server_token}>"

    def _setup_managers(self):
        """Allows to access manager by model name.

        >>> postmark = PostmarkClient(server_token='TEST')
        >>> postmark.bounces
        <BounceManager>
        """
        for manager_class in self._managers:
            instance = manager_class(self)
            setattr(self, instance.name, instance)

    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = requests.Session()  # pylint: disable=attribute-defined-outside-init
            adapter = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def call(self, method, endpoint, token_type="server", data=None, **kwargs):
        if token_type == "account":
            header = "X-Postmark-Account-Token"
            token = self.account_token
        else:
            header = "X-Postmark-Server-Token"
            token = self.server_token
        return self._call(method, self.root_api_url, endpoint, data, {header: token}, **kwargs)

    def call_status(self, endpoint):
        return self._call("GET", STATUS_API, endpoint)

    def spamcheck(self, dump, options="long"):
        data = {"email": dump, "options": options}
        response = self._call("POST", SPAMCHECK_API, "", data)
        if not response["success"]:
            raise SpamAssassinError(response["message"])
        return response

    def _call(self, method, root, endpoint, data=None, headers=None, **kwargs):
        default_headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
        if headers:
            default_headers.update(headers)
        url = urljoin(root, endpoint)
        self.logger.debug("Request: %s %s, Data: %s", method, url, data)
        response = self.session.request(
            method,
            url,
            json=data,
            params=kwargs,
            headers=default_headers,
            timeout=self.timeout,
        )
        self.logger.debug("Response: %s", response.text)
        self.check_response(response)
        return response.json()

    def check_response(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            try:
                data = response.json()
            except ValueError as exc:
                raise http_error from exc
            message = self.format_exception_message(data)
            raise ClientError(message, error_code=data["ErrorCode"]) from http_error

    def format_exception_message(self, data):
        return "[{}] {}".format(data["ErrorCode"], data["Message"])
