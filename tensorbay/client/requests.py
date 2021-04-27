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
from threading import Lock
from typing import (
    Any,
    Callable,
    DefaultDict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
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
from ..exception import ResponseError, ResponseErrorDistributor
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
    ) -> Response:  # noqa: DAR401
        """Make the request.

        Arguments:
            method: Method for the request.
            url: URL for the request.
            *args: Extra arguments to make the request.
            **kwargs: Extra keyword arguments to make the request.

        Returns:
            Response of the request.

        Raises:  # noqa: DAR402
            ResponseError: If post response error.

        """
        try:
            response = super().request(method, url, *args, **kwargs)
            if response.status_code not in (200, 201):
                logger.error(
                    "Unexpected status code(%d)!%s", response.status_code, ResponseLogging(response)
                )
                error_code = response.json()["code"]
                raise ResponseErrorDistributor.get(error_code, ResponseError)(response)
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


PagingGenerator = Callable[[int, int], Generator[_T, None, int]]


class LazyItem(Generic[_T]):  # pylint: disable=too-few-public-methods
    """In paging lazy evaluation system, a LazyItem instance represents an element in a pagination.

    If user wants to access the elememt, LazyItem will trigger the paging request to pull a page of
    elements and return the required element. All the pulled elements will be stored in different
    LazyItem instances and will not be requested again.

    Arguments:
        page: The page the item belongs to.

    """

    __slots__ = ("data", "_page")

    data: _T

    def __init__(self, page: "LazyPage[_T]"):
        self._page = page

    def get(self) -> _T:
        """Access the actual element represented by LazyItem.

        If the element is already pulled from web, it will be return directly, otherwise this
        function will request for a page of elements to get the required elememt.

        Returns:
            The actual element this LazyItem instance represents.

        """
        if not hasattr(self, "data"):
            self._page.pull()

        return self.data


class LazyPage(Generic[_T]):  # pylint: disable=too-few-public-methods
    """In paging lazy evaluation system, a LazyPage instance represents a page with elements.

    LazyPage is used for sending paging request to pull a page of elements and storing them in
    different :class:`LazyItem` instances.

    Arguments:
        offset: The offset of the page.
        limit: The limit of the page.
        func: A paging generator function, which takes offset<int> and limit<int> as inputs and
            returns a generator. The returned generator should yield the element user needs, and
            return the total count of the elements in the paging request.

    """

    __slots__ = ("_offset", "_limit", "_func", "_lock", "_total_count", "items")

    def __init__(self, offset: int, limit: int, func: PagingGenerator[_T]) -> None:
        self._offset = offset
        self._limit = limit
        self._func = func
        self._lock = Lock()
        self._total_count: Optional[int] = None

        self.items: Tuple[LazyItem[_T], ...] = tuple(LazyItem(self) for _ in range(limit))

    def pull(self) -> int:
        """Send paging request to pull a page of elements and store them in :class:`LazyItem`.

        Returns:
            The totalCount of all elements.

        """
        with self._lock:
            if self._total_count is None:
                iterator = zip(self._func(self._offset, self._limit), self.items)
                try:
                    while True:
                        data, item = next(iterator)
                        item.data = data
                except StopIteration as error:
                    self._total_count = error.value

            return self._total_count


class PagingList(Sequence[_T], ReprMixin):  # pylint: disable=too-many-ancestors
    """PagingList is a wrap of web paging request.

    It follows the python Sequence protocal, which means it can be used like a python builtin list.
    And it provides features like lazy evaluation and cache.

    Arguments:
        func: A paging generator function, which takes offset<int> and limit<int> as inputs and
            returns a generator. The returned generator should yield the element user needs, and
            return the total count of the elements in the paging request.
        limit: The page size of each paging request.

    """

    _S = TypeVar("_S", bound="PagingList[_T]")

    _repr_type = ReprType.SEQUENCE

    _items: List[LazyItem[_T]]

    def __init__(self, func: PagingGenerator[_T], limit: int) -> None:
        self._func = func
        self._limit = limit
        self._lock = Lock()
        self._init_items: Callable[[int], List[LazyItem[_T]]] = self._init_all_items

    def __len__(self) -> int:
        return self._get_data().__len__()

    @overload
    def __getitem__(self: _S, index: int) -> _T:
        ...

    @overload
    def __getitem__(self: _S, index: slice) -> _S:
        ...

    def __getitem__(self: _S, index: Union[int, slice]) -> Union[_T, _S]:
        if isinstance(index, slice):
            return self._get_slice(index)

        return self._get_data(index)[index].get()

    def _init_all_items(self, index: int = 0) -> List[LazyItem[_T]]:
        index_offset = index // self._limit * self._limit
        index_page = LazyPage(index_offset, self._limit, self._func)
        total_count = index_page.pull()
        items: List[LazyItem[_T]] = []
        for offset, limit in self._range(total_count, self._limit):
            page = index_page if offset == index_offset else LazyPage(offset, limit, self._func)
            items.extend(page.items)

        return items

    def _get_data(self, index: int = 0) -> List[LazyItem[_T]]:
        if not hasattr(self, "_items"):
            acquire = self._lock.acquire(blocking=False)
            try:
                if acquire:
                    index = index if index >= 0 else 0
                    self._items = self._init_items(index)
                else:
                    self._lock.acquire()
            finally:
                self._lock.release()

        return self._items

    def _get_slice(self: _S, slicing: slice) -> _S:
        paging_list = self.__class__(self._func, self._limit)
        if hasattr(self, "_items"):
            paging_list._items = self._items[slicing]  # pylint: disable=protected-access
        else:
            paging_list._init_items = (  # pylint: disable=protected-access
                lambda index: self._get_data()[slicing]
            )

        return paging_list

    @staticmethod
    def _range(total_count: int, limit: int) -> Iterator[Tuple[int, int]]:
        """A Generator which generates offset and limit for paging request.

        Examples:
            >>> self._range(10, 3)
            <generator object paging_range at 0x11b9932e0>

            >>> list(self._range(10, 3))
            [(0, 3), (3, 3), (6, 3), (9, 1)]

        Arguments:
            total_count: The total count of the page.
            limit: The paging limit.

        Yields:
            The tuple (offset, limit) for paging request.

        """
        div, mod = divmod(total_count, limit)
        yield from zip_longest(range(0, total_count, limit), repeat(limit, div), fillvalue=mod)
