from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TextIO
from urllib.parse import urljoin

import requests

from . import __version__
from .exceptions import ClientError, SpamAssassinError
from .logging import get_logger
from .models.base import BaseModelManager, attach_managers

# Importable from here before the async client; kept for existing imports
from .models.base import ModelManager as ModelManager
from .models.bounces import AsyncBounceManager, BounceManager
from .models.domains import AsyncDomainsManager, DomainsManager
from .models.emails import AsyncEmailManager, EmailManager
from .models.message_streams import AsyncMessageStreamsManager, MessageStreamsManager
from .models.messages import AsyncMessageManager, MessageManager
from .models.senders import AsyncSenderSignaturesManager, SenderSignaturesManager
from .models.server import AsyncServerManager, ServerManager
from .models.servers import AsyncServersManager, ServersManager
from .models.stats import AsyncStatsManager, StatsManager
from .models.status import AsyncStatusManager, StatusManager
from .models.suppressions import AsyncSuppressionsManager, SuppressionsManager
from .models.templates import AsyncTemplateManager, TemplateManager
from .models.triggers import AsyncTriggersManager, TriggersManager
from .utils import get_args

if TYPE_CHECKING:
    import httpx2
    from css_inline import CSSInliner

DEFAULT_API = "https://api.postmarkapp.com/"
STATUS_API = "https://status.postmarkapp.com/api/1.0/"
SPAMCHECK_API = "https://spamcheck.postmarkapp.com/filter/"
USER_AGENT = f"Postmarker/{__version__}"
TEST_TOKEN = "POSTMARK_API_TEST"


def make_css_inliner(inline_css: bool | CSSInliner) -> CSSInliner | None:
    if not inline_css:
        return None
    if inline_css is not True:
        return inline_css
    try:
        import css_inline
    except ImportError as exc:
        raise ImportError(
            "`inline_css` requires the `css-inline` package: pip install 'postmarker[css-inline]'"
        ) from exc
    # Email HTML may carry user content; never fetch `<link>` URLs from it
    return css_inline.CSSInliner(load_remote_stylesheets=False)


class BaseClient:
    """Shared, transport-independent part of the sync and async clients."""

    _managers: tuple[type[BaseModelManager[Any]], ...] = ()

    def __init__(
        self,
        server_token: str | None = None,
        account_token: str | None = None,
        verbosity: int = 0,
        max_retries: int = 0,
        timeout: float | tuple[float, float] | None = None,
        logs_stream: TextIO = sys.stdout,
        root_api_url: str = DEFAULT_API,
        inline_css: bool | CSSInliner = False,
    ) -> None:
        assert server_token or account_token, "You have to provide server_token or account_token to use Postmark API"
        self.server_token = server_token
        self.account_token = account_token
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = get_logger("Postmarker", verbosity, logs_stream)
        self.root_api_url = root_api_url
        self.css_inliner = make_css_inliner(inline_css)
        self._setup_managers()

    @classmethod
    def from_config(cls, config: Mapping[str, Any], prefix: str = "postmark_", is_uppercase: bool = False) -> Self:
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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.server_token}>"

    def _setup_managers(self) -> None:
        """Allows to access manager by model name.

        >>> postmark = PostmarkClient(server_token='TEST')
        >>> postmark.bounces
        <BounceManager>
        """
        attach_managers(self, self, self._managers)

    def _token_headers(self, token_type: str) -> dict[str, str | None]:
        if token_type == "account":
            return {"X-Postmark-Account-Token": self.account_token}
        return {"X-Postmark-Server-Token": self.server_token}

    def _request_headers(self, headers: dict[str, str | None] | None) -> dict[str, str | None]:
        default_headers: dict[str, str | None] = {"Accept": "application/json", "User-Agent": USER_AGENT}
        if headers:
            default_headers.update(headers)
        return default_headers

    def format_exception_message(self, data: dict[str, Any]) -> str:
        return "[{}] {}".format(data["ErrorCode"], data["Message"])


class PostmarkClient(BaseClient):
    """Basic class for API clients. Provides basic functionality to make requests."""

    bounces: BounceManager
    domains: DomainsManager
    emails: EmailManager
    messages: MessageManager
    message_streams: MessageStreamsManager
    senders: SenderSignaturesManager
    server: ServerManager
    servers: ServersManager
    stats: StatsManager
    status: StatusManager
    suppressions: SuppressionsManager
    templates: TemplateManager
    triggers: TriggersManager
    _session: requests.Session

    _managers = (
        BounceManager,
        DomainsManager,
        EmailManager,
        MessageManager,
        MessageStreamsManager,
        SenderSignaturesManager,
        ServerManager,
        ServersManager,
        StatsManager,
        StatusManager,
        SuppressionsManager,
        TemplateManager,
        TriggersManager,
    )

    @property
    def session(self) -> requests.Session:
        if not hasattr(self, "_session"):
            self._session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def call(self, method: str, endpoint: str, token_type: str = "server", data: Any = None, **kwargs: Any) -> Any:
        return self._call(method, self.root_api_url, endpoint, data, self._token_headers(token_type), **kwargs)

    def call_status(self, endpoint: str) -> Any:
        return self._call("GET", STATUS_API, endpoint)

    def spamcheck(self, dump: str, options: str = "long") -> Any:
        data = {"email": dump, "options": options}
        response = self._call("POST", SPAMCHECK_API, "", data)
        if not response["success"]:
            raise SpamAssassinError(response["message"])
        return response

    def _call(
        self,
        method: str,
        root: str,
        endpoint: str,
        data: Any = None,
        headers: dict[str, str | None] | None = None,
        **kwargs: Any,
    ) -> Any:
        url = urljoin(root, endpoint)
        self.logger.debug("Request: %s %s, Data: %s", method, url, data)
        response = self.session.request(
            method,
            url,
            json=data,
            params=kwargs,
            headers=self._request_headers(headers),
            timeout=self.timeout,
        )
        self.logger.debug("Response: %s", response.text)
        self.check_response(response)
        return response.json()

    def check_response(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            try:
                data = response.json()
            except ValueError as exc:
                raise http_error from exc
            message = self.format_exception_message(data)
            raise ClientError(message, error_code=data["ErrorCode"]) from http_error


class AsyncPostmarkClient(BaseClient):
    """Async twin of :py:class:`PostmarkClient`: every method that makes a request is a coroutine."""

    bounces: AsyncBounceManager
    domains: AsyncDomainsManager
    emails: AsyncEmailManager
    messages: AsyncMessageManager
    message_streams: AsyncMessageStreamsManager
    senders: AsyncSenderSignaturesManager
    server: AsyncServerManager
    servers: AsyncServersManager
    stats: AsyncStatsManager
    status: AsyncStatusManager
    suppressions: AsyncSuppressionsManager
    templates: AsyncTemplateManager
    triggers: AsyncTriggersManager
    _session: httpx2.AsyncClient

    _managers = (
        AsyncBounceManager,
        AsyncDomainsManager,
        AsyncEmailManager,
        AsyncMessageManager,
        AsyncMessageStreamsManager,
        AsyncSenderSignaturesManager,
        AsyncServerManager,
        AsyncServersManager,
        AsyncStatsManager,
        AsyncStatusManager,
        AsyncSuppressionsManager,
        AsyncTemplateManager,
        AsyncTriggersManager,
    )
    # Tests replace the transport before the first request
    _transport: httpx2.AsyncBaseTransport | None = None

    def __init__(
        self,
        server_token: str | None = None,
        account_token: str | None = None,
        verbosity: int = 0,
        max_retries: int = 0,
        timeout: float | tuple[float, float] | None = None,
        logs_stream: TextIO = sys.stdout,
        root_api_url: str = DEFAULT_API,
        inline_css: bool | CSSInliner = False,
    ) -> None:
        try:
            import httpx2  # noqa: F401
        except ImportError as exc:
            raise ImportError("`AsyncPostmarkClient` requires `httpx2`: uv pip install 'postmarker[async]'") from exc
        super().__init__(
            server_token, account_token, verbosity, max_retries, timeout, logs_stream, root_api_url, inline_css
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if hasattr(self, "_session"):
            await self._session.aclose()
            # The next request opens a new pool, so the client survives several `async with` blocks
            del self._session

    @property
    def session(self) -> httpx2.AsyncClient:
        if not hasattr(self, "_session"):
            import httpx2

            # Private helper: httpx2 skips env proxies when given a transport, and this keeps its rules
            from httpx2._utils import get_environment_proxies

            mounts: dict[str, httpx2.AsyncBaseTransport | None] = {}
            if self._transport is None:
                # httpx2 drops `retries` for proxies
                mounts = {
                    key: None if url is None else httpx2.AsyncHTTPTransport(proxy=url)
                    for key, url in get_environment_proxies().items()
                }
            self._session = httpx2.AsyncClient(
                transport=self._transport or httpx2.AsyncHTTPTransport(retries=self.max_retries),
                mounts=mounts,
                follow_redirects=True,
            )
        return self._session

    async def call(
        self, method: str, endpoint: str, token_type: str = "server", data: Any = None, **kwargs: Any
    ) -> Any:
        return await self._call(method, self.root_api_url, endpoint, data, self._token_headers(token_type), **kwargs)

    async def call_status(self, endpoint: str) -> Any:
        return await self._call("GET", STATUS_API, endpoint)

    async def spamcheck(self, dump: str, options: str = "long") -> Any:
        data = {"email": dump, "options": options}
        response = await self._call("POST", SPAMCHECK_API, "", data)
        if not response["success"]:
            raise SpamAssassinError(response["message"])
        return response

    async def _call(
        self,
        method: str,
        root: str,
        endpoint: str,
        data: Any = None,
        headers: dict[str, str | None] | None = None,
        **kwargs: Any,
    ) -> Any:
        url = urljoin(root, endpoint)
        self.logger.debug("Request: %s %s, Data: %s", method, url, data)
        response = await self._request(
            method,
            url,
            json=data,
            params=kwargs,
            headers=self._request_headers(headers),
            timeout=self.timeout,
        )
        self.logger.debug("Response: %s", response.text)
        self.check_response(response)
        return response.json()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        json: Any,
        params: dict[str, Any],
        headers: dict[str, str | None],
        timeout: float | tuple[float, float] | None,
    ) -> httpx2.Response:
        import httpx2

        # Encode like requests: skip `None` values, bools as `True` / `False`
        encoded_params = {
            key: str(value) if isinstance(value, bool) else value for key, value in params.items() if value is not None
        }
        present_headers = {key: value for key, value in headers.items() if value is not None}
        request_timeout: float | httpx2.Timeout | None
        if isinstance(timeout, tuple):
            connect, read = timeout
            request_timeout = httpx2.Timeout(connect=connect, read=read, write=read, pool=connect)
        else:
            request_timeout = timeout
        # Merge into a query already in `url`, as requests does; httpx2 would replace it
        return await self.session.request(
            method,
            httpx2.URL(url).copy_merge_params(encoded_params),
            json=json,
            headers=present_headers,
            timeout=request_timeout,
        )

    def check_response(self, response: httpx2.Response) -> None:
        import httpx2

        try:
            response.raise_for_status()
        except httpx2.HTTPStatusError as http_error:
            try:
                data = response.json()
            except ValueError as exc:
                raise http_error from exc
            message = self.format_exception_message(data)
            raise ClientError(message, error_code=data["ErrorCode"]) from http_error
