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
from typing import Any, Callable, DefaultDict, Iterable, Optional, TypeVar
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.models import PreparedRequest, Response
from tqdm import tqdm
from urllib3.util.retry import Retry

from ..__verison__ import __version__
from ..exception import ResponseError, ResponseErrorDistributor
from .log import RequestLogging, ResponseLogging

logger = logging.getLogger(__name__)


class Config:  # pylint: disable=too-few-public-methods
    """This is a base class defining the concept of Request Config.

    Attributes:
        max_retries: Maximum retry times of the request.
        allowed_retry_methods: The allowed methods for retrying request.
        allowed_retry_status: The allowed status for retrying request.
            If both methods and status are fitted, the retrying strategy will work.
        timeout: Timeout value of the request in seconds.
        is_internal: Whether the request is from internal.

    """

    def __init__(self) -> None:

        self.max_retries = 3
        self.allowed_retry_methods = ["HEAD", "OPTIONS", "POST", "PUT"]
        self.allowed_retry_status = [429, 500, 502, 503, 504]

        self.timeout = 30
        self.is_internal = False
        self._x_source = "PYTHON-SDK"


config = Config()


class TimeoutHTTPAdapter(HTTPAdapter):
    """This class defines the http adapter for setting the timeout value.

    Arguments:
        *args: Extra arguments to initialize TimeoutHTTPAdapter.
        timeout: Timeout value of the post request in seconds.
        **kwargs: Extra keyword arguments to initialize TimeoutHTTPAdapter.

    """

    def __init__(self, *args: Any, timeout: Optional[int] = None, **kwargs: Any) -> None:
        self.timeout = timeout if timeout is not None else config.timeout
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
            total=config.max_retries,
            status_forcelist=config.allowed_retry_status,
            allowed_methods=config.allowed_retry_methods,
            raise_on_status=False,
        )

        self.mount("http://", TimeoutHTTPAdapter(20, 20, retry_strategy))
        self.mount("https://", TimeoutHTTPAdapter(20, 20, retry_strategy))

    def request(  # type: ignore[override]  # pylint: disable=signature-differs
        self, method: str, url: str, *args: Any, **kwargs: Any
    ) -> Response:  # noqa: DAR401
        """Make the request.

        Arguments:
            method: Method for the request.
            url: URL for the request.
            *args: Extra arguments to make the request.
            **kwargs: Extra keyword arguments to make the request.

        Returns:
            Response of the request.

        Raises:
            ResponseError: If post response error.

        """
        try:
            response = super().request(method, url, *args, **kwargs)
            if response.status_code not in (200, 201):
                logger.error(
                    "Unexpected status code(%d)!%s", response.status_code, ResponseLogging(response)
                )
                raise ResponseError(response)

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
            if section:
                url = urljoin(self._open_api, section)
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

        Raises:
            ResponseError: When the status code OpenAPI returns is unexpected.

        Returns:
            Response of the request.

        """
        kwargs.setdefault("headers", {})["X-Token"] = self.access_key
        kwargs["headers"][
            "X-Source"
        ] = f"{config._x_source}/{__version__}"  # pylint: disable=protected-access

        try:
            return self.do(method=method, url=self._url_make(section, dataset_id), **kwargs)
        except ResponseError as error:
            response = error.response
            error_code = response.json()["code"]
            raise ResponseErrorDistributor.get(error_code, ResponseError)(response) from None

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


class Tqdm(tqdm):  # type: ignore[misc]
    """A wrapper class of tqdm for showing the process bar.

    Arguments:
        total: The number of excepted iterations.
        disable: Whether to disable the entire progress bar.

    """

    def __init__(self, total: int, disable: bool = False) -> None:
        super().__init__(desc="Uploading", total=total, disable=disable)

    def update_callback(self, _: Any) -> None:
        """Callback function for updating process bar when multithread task is done."""
        self.update()

    def update_for_skip(self, condition: bool) -> bool:
        """Update process bar for the items which are skipped in builtin filter function.

        Arguments:
            condition: The filter condition, the process bar will be updated if condition is False.

        Returns:
            The input condition.

        """
        if not condition:
            self.update()

        return condition


def multithread_upload(
    function: Callable[[_T], None],
    arguments: Iterable[_T],
    *,
    jobs: int = 1,
    pbar: Tqdm,
) -> None:
    """Multi-thread upload framework.

    Arguments:
        function: The upload function.
        arguments: The arguments of the upload function.
        jobs: The number of the max workers in multi-thread uploading procession.
        pbar: The :class:`Tqdm` instance for showing the upload process bar.

    """
    with ThreadPoolExecutor(jobs) as executor:
        futures = [executor.submit(function, argument) for argument in arguments]
        for future in futures:
            future.add_done_callback(pbar.update_callback)

        done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
        for future in not_done:
            future.cancel()
        for future in done:
            future.result()
