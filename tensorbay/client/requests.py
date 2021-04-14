#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class Client and method multithread_upload.

:class:`Client` can send POST, PUT, and GET requests to the TensorBay Dataset Open API.

:meth:`multithread_upload` creates a multi-thread framework for uploading.

"""

import logging
import os
from collections import defaultdict
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from itertools import repeat, zip_longest
from typing import Any, Callable, DefaultDict, Iterable, Iterator, Optional, Tuple, TypeVar
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.models import PreparedRequest, Response
from urllib3.util.retry import Retry

from ..__verison__ import __version__
from .exceptions import GASResponseError
from .log import RequestLogging, ResponseLogging

logger = logging.getLogger(__name__)


class Config:  # pylint: disable=too-few-public-methods
    """This is a base class defining the concept of Request Config."""

    def __init__(self) -> None:

        self.max_retries = 3
        self.allowed_retry_methods = ["HEAD", "OPTIONS", "POST", "PUT"]
        self.allowed_retry_status = [429, 500, 502, 503, 504]

        self.timeout = 30
        self._is_intern = False
        self._x_source = "PYTHON-SDK"

    @property
    def is_intern(self) -> bool:
        """Get whether the request is from intern.

        Returns:
            Whether the request is from intern.

        """
        return self._is_intern


default_config = Config()


class TimeoutHTTPAdapter(HTTPAdapter):
    """This class defines the http adapter for setting the timeout value.

    Arguments:
        *args: Extra arguments to initialize TimeoutHTTPAdapter.
        timeout: Timeout value of the post request in seconds.
        **kwargs: Extra keyword arguments to initialize TimeoutHTTPAdapter.

    """

    def __init__(self, *args: Any, timeout: Optional[int] = None, **kwargs: Any) -> None:
        self.timeout = timeout if timeout is not None else default_config.timeout
        super().__init__(*args, **kwargs)

    def send(  # pylint: disable=too-many-arguments
        self,
        request: PreparedRequest,
        stream: Any = False,
        timeout: Any = None,
        verify: Any = True,
        cert: Any = None,
        proxies: Any = None,
    ) -> Any:
        """Send the request.

        Arguments:
            request: The PreparedRequest being sent.
            stream: Whether to stream the request content.
            timeout: Timeout value of the post request in seconds.
            verify: A path string to a CA bundle to use or
                a boolean which controls whether to verify the server's TLS certificate.
            cert: User-provided SSL certificate.
            proxies: Proxies dict applying to the request.

        Returns:
            Response object.

        """
        if timeout is None:
            timeout = self.timeout
        return super().send(request, stream, timeout, verify, cert, proxies)


class UserSession(Session):  # pylint: disable=too-few-public-methods
    """This class defines UserSession."""

    def __init__(self) -> None:
        super().__init__()
        # self.session.hooks["response"] = [logging_hook]

        retry_strategy = Retry(
            total=default_config.max_retries,
            status_forcelist=default_config.allowed_retry_status,
            method_whitelist=default_config.allowed_retry_methods,
            raise_on_status=False,
        )

        self.mount("http://", TimeoutHTTPAdapter(20, 20, retry_strategy))
        self.mount("https://", TimeoutHTTPAdapter(20, 20, retry_strategy))

    def request(  # type: ignore[override]  # pylint: disable=signature-differs
        self, method: str, url: str, *args: Any, **kwargs: Any
    ) -> Response:
        """Make the request.

        Arguments:
            method: Method for the request.
            url: URL for the request.
            *args: Extra arguments to make the request.
            **kwargs: Extra keyword arguments to make the request.

        Returns:
            Response of the request.

        Raises:
            GASResponseError: If post response error.

        """
        try:
            response = super().request(method, url, *args, **kwargs)
            if response.status_code not in (200, 201):
                logger.error("Invalid state code!%s", ResponseLogging(response))
                raise GASResponseError(response)
            logger.debug(ResponseLogging(response))
            return response

        except RequestException as error:
            logger.error(
                "%s.%s: %s%s",
                error.__class__.__module__,
                error.__class__.__name__,
                error,
                RequestLogging(error.request),
            )
            raise


class Client:
    """This class defines :class:`Client`.

    :class:`Client` defines the client that saves the user and URL information
    and supplies basic call methods that will be used by derived clients,
    such as sending GET, PUT and POST requests to TensorBay Open API.

    Arguments:
        access_key: User's access key.
        url: The URL of the graviti gas website.

    """

    _DEFAULT_URL_CN = "https://gas.graviti.cn/"
    _DEFAULT_URL_COM = "https://gas.graviti.com/"

    def __init__(self, access_key: str, url: str = "") -> None:
        if access_key.startswith("Accesskey-"):
            url = url if url else Client._DEFAULT_URL_CN
        elif access_key.startswith("ACCESSKEY-"):
            url = url if url else Client._DEFAULT_URL_COM
        else:
            raise TypeError("Wrong accesskey format!")

        if not url.startswith("https://"):
            raise TypeError("Invalid url, only support url starts with 'https://'")

        self.gateway_url = urljoin(url, "gatewayv2/")
        self.access_key = access_key

        self._sessions: DefaultDict[int, UserSession] = defaultdict(UserSession)
        self._open_api = urljoin(self.gateway_url, "tensorbay-open-api/v1/")

    def _url_make(self, section: str, dataset_id: str = "") -> str:
        """Generate Open API URL.

        Arguments:
            section: The section of the request.
            dataset_id: Dataset ID.

        Returns:
             Open API URL.

        """
        if dataset_id:
            dataset_url = urljoin(self._open_api, "datasets/")
            if section:
                url = urljoin(urljoin(dataset_url, dataset_id + "/"), section)
            else:
                url = urljoin(dataset_url, dataset_id)
        else:
            url = urljoin(self._open_api, "datasets")
        return url

    @property
    def session(self) -> UserSession:
        """Create and return a session per PID so each sub-processes will use their own session.

        Returns:
            The session corresponding to the process.
        """
        return self._sessions[os.getpid()]

    def open_api_do(
        self, method: str, section: str, dataset_id: str = "", **kwargs: Any
    ) -> Response:
        """Send a request to the TensorBay Open API.

        Arguments:
            method: The method of the request.
            section: The section of the request.
            dataset_id: Dataset ID.
            **kwargs: Extra keyword arguments to send in the POST request.

        Returns:
            Response of the request.

        """
        kwargs.setdefault("headers", {})["X-Token"] = self.access_key
        kwargs["headers"][
            "X-Source"
        ] = f"{default_config._x_source}/{__version__}"  # pylint: disable=protected-access

        return self.do(method=method, url=self._url_make(section, dataset_id), **kwargs)

    def do(self, method: str, url: str, **kwargs: Any) -> Response:  # pylint: disable=invalid-name
        """Send a request.

        Arguments:
            method: The method of the request.
            url: The URL of the request.
            **kwargs: Extra keyword arguments to send in the GET request.

        Returns:
            Response of the request.

        """
        return self.session.request(method=method, url=url, **kwargs)


_T = TypeVar("_T")


def multithread_upload(
    function: Callable[[_T], None],
    arguments: Iterable[_T],
    *,
    jobs: int = 1,
) -> None:
    """Multi-thread upload framework.

    Arguments:
        function: The upload function.
        arguments: The arguments of the upload function.
        jobs: The number of the max workers in multi-thread uploading procession.

    """
    with ThreadPoolExecutor(jobs) as executor:
        futures = [executor.submit(function, argument) for argument in arguments]

        done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
        for future in not_done:
            future.cancel()
        for future in done:
            future.result()


def paging_range(start: int, stop: int, limit: int) -> Iterator[Tuple[int, int]]:
    """A Generator which generates offset and limit for paging request.

    Examples:
        >>> paging_range(0, 10, 3)
        <generator object paging_range at 0x11b9932e0>

        >>> list(paging_range(0, 10, 3))
        [(0, 3), (3, 3), (6, 3), (9, 1)]

    Arguments:
        start: The paging index to start.
        stop: The paging index to end.
        limit: The paging limit.

    Yields:
        The tuple (offset, limit) for paging request.

    """
    div, mod = divmod(stop - start, limit)
    yield from zip_longest(range(start, stop, limit), repeat(limit, div), fillvalue=mod)
