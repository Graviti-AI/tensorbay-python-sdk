#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The implementation of request related tools."""

import logging
import os
from collections import defaultdict
from typing import Any, DefaultDict, Optional

import urllib3
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, StreamConsumedError
from requests.models import PreparedRequest, Response
from tqdm import tqdm
from urllib3.util.retry import Retry

from tensorbay.client.log import RequestLogging, ResponseLogging
from tensorbay.exception import ResponseError

logger = logging.getLogger(__name__)


_CHUNK_SIZE = 8 * 1024


def _get_allowed_methods_keyword() -> str:
    splits = urllib3.__version__.split(".", 2)
    major = int(splits[0])
    minor = int(splits[1])
    return "allowed_methods" if (major, minor) >= (1, 26) else "method_whitelist"


# check the version of urllib3 and choose the correct keyword for "allowed_methods" in "Retry"
_ALLOWED_METHODS = _get_allowed_methods_keyword()


class Config:
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


class UserSession(Session):
    """This class defines UserSession."""

    def __init__(self) -> None:
        super().__init__()
        # self.session.hooks["response"] = [logging_hook]

        retry_strategy = Retry(
            total=config.max_retries,
            status_forcelist=config.allowed_retry_status,
            raise_on_status=False,
            **{_ALLOWED_METHODS: config.allowed_retry_methods},
        )

        self.mount("http://", TimeoutHTTPAdapter(20, 20, retry_strategy))
        self.mount("https://", TimeoutHTTPAdapter(20, 20, retry_strategy))

    def request(  # type: ignore[override]
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
                raise ResponseError(response=response)

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


SESSIONS: DefaultDict[int, UserSession] = defaultdict(UserSession)


def get_session() -> UserSession:
    """Create and return a session per PID so each sub-processes will use their own session.

    Returns:
        The session corresponding to the process.
    """
    return SESSIONS[os.getpid()]


class UserResponse:
    """This class used to read data from Response with stream method.

    Arguments:
        response: Response of the Session.request().

    """

    def __init__(self, response: Response):
        self.response = response

    def __enter__(self) -> "UserResponse":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the response."""
        self.response.close()

    def read(self, amt: Optional[int] = None) -> bytes:
        """Read data from response.

        Arguments:
            amt: The needed read amount.

        Returns:
            Response of the request.

        """
        if amt is None:
            try:
                return b"".join(chunk for chunk in self.response.iter_content(_CHUNK_SIZE))

            except StreamConsumedError:
                return b""

        try:
            return next(self.response.iter_content(amt))  # type: ignore[no-any-return]

        except StopIteration:
            return b""


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
