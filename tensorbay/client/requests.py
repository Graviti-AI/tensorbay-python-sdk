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
from itertools import count
from threading import Lock
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    Optional,
    Sequence,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.models import PreparedRequest, Response
from urllib3.util.retry import Retry

from ..__verison__ import __version__
from ..exception import ResponseError
from ..utility import ReprMixin, ReprType
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
            method_whitelist=config.allowed_retry_methods,
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

        Returns:
            Response of the request.

        """
        kwargs.setdefault("headers", {})["X-Token"] = self.access_key
        kwargs["headers"][
            "X-Source"
        ] = f"{config._x_source}/{__version__}"  # pylint: disable=protected-access

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


class PagingList(Sequence[_T], ReprMixin):  # pylint: disable=too-many-ancestors
    """PagingList is a wrap of web paging request.

    It follows the python Sequence protocal, which means it can be used like a python builtin list.
    And it provides features like lazy evaluation and cache.

    Arguments:
        func: A paging generator function, which inputs offset<int> and limit<int> and returns a
            generator. The returned generator should yield the element user needs, and return the
            total count of the elements in the paging request.
        limit: The page size of each paging request.
        slicing: The required slice of PagingList.

    """

    _S = TypeVar("_S", bound="PagingList[_T]")
    _K = TypeVar("_K")

    _repr_type = ReprType.SEQUENCE

    def __init__(
        self,
        func: Callable[[int, int], Generator[_T, None, int]],
        limit: int,
        slicing: slice = slice(0, None),
    ) -> None:
        self._data: Dict[int, _T] = {}
        self._attr: Dict[str, int] = {}
        self._locks: DefaultDict[Union[int, str], Lock] = defaultdict(Lock)
        self._func = func
        self._limit = limit

        if slicing.step is not None:
            raise ValueError("The step slice is not supported yet.")

        self._slice = slicing
        self._len: Optional[int] = None

    def __len__(self) -> int:
        return self._get_len()

    @overload
    def __getitem__(self: _S, index: int) -> _T:
        ...

    @overload
    def __getitem__(self: _S, index: slice) -> _S:
        ...

    def __getitem__(self: _S, index: Union[int, slice]) -> Union[_T, _S]:
        if isinstance(index, slice):
            return self._get_slice(index)

        index = self._make_index_positive(index)
        if index < 0 or index >= self._get_len(index):
            raise IndexError("list index out of range")

        paging_index = self._slice.start + index
        if paging_index not in self._data:
            offset = self._get_offset(paging_index)
            self._call_with_lock(offset, self._extend, offset)

        return self._data[paging_index]

    def _extend(self, offset: int) -> int:
        generator = self._func(offset, self._limit)
        try:
            for i in count(offset):
                data = next(generator)
                self._data[i] = data
        except StopIteration as error:
            return error.value  # type: ignore[no-any-return]

        raise TypeError("Impossible to be here, add this to make pylint and mypy happy")

    def _get_total_count(self, index: int) -> None:
        offset = self._get_offset(index)
        self._attr["totalCount"] = self._extend(offset)

    def _get_len(self, index: int = 0) -> int:
        if self._len is None:
            if "totalCount" not in self._attr:
                self._call_with_lock("totalCount", self._get_total_count, index)

            total_count = self._attr["totalCount"]
            stop = total_count if self._slice.stop is None else min(total_count, self._slice.stop)
            start = min(total_count, self._slice.start)
            self._len = stop - start

        return self._len

    def _make_index_positive(self, index: int) -> int:
        return index if index >= 0 else self._get_len() + index

    def _get_offset(self, index: int) -> int:
        return index // self._limit * self._limit

    def _call_with_lock(self, key: Union[int, str], func: Callable[[_K], Any], arg: _K) -> None:
        lock = self._locks[key]
        acquire = lock.acquire(blocking=False)
        try:
            if acquire:
                func(arg)
                del self._locks[key]
            else:
                lock.acquire()
        finally:
            lock.release()

    def _get_slice(self: _S, input_slice: slice) -> _S:
        start = self._slice.start
        if input_slice.start is not None:
            start += self._make_index_positive(input_slice.start)

        stop = input_slice.stop
        if stop is not None:
            stop = self._make_index_positive(stop) + self._slice.start

        paging_list = self.__class__(self._func, self._limit, slice(start, stop))

        # The sliced PagingList shares the "_data", "_attr" and "_locks" with the root PagingList
        paging_list._data = self._data  # pylint: disable=protected-access
        paging_list._attr = self._attr  # pylint: disable=protected-access
        paging_list._locks = self._locks  # pylint: disable=protected-access

        return paging_list
