#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The multi-thread uploading framework and request senders of the TensorBay Dataset Open API."""

import logging
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from queue import Queue
from threading import Lock
from typing import Any, Callable, Generic, Iterable, Optional, Tuple, TypeVar
from urllib.parse import urljoin
from uuid import uuid4

from requests.models import Response

from tensorbay.__version__ import __version__
from tensorbay.exception import ResponseError, ResponseErrorDistributor
from tensorbay.utility import Tqdm, config, get_session

logger = logging.getLogger(__name__)


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

    @staticmethod
    def do(method: str, url: str, **kwargs: Any) -> Response:  # pylint: disable=invalid-name
        """Send a request.

        Arguments:
            method: The method of the request.
            url: The URL of the request.
            **kwargs: Extra keyword arguments to send in the GET request.

        Returns:
            Response of the request.

        """
        return get_session().request(method=method, url=url, **kwargs)

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
        headers = kwargs.setdefault("headers", {})
        headers["X-Token"] = self.access_key
        headers[
            "X-Source"
        ] = f"{config._x_source}/{__version__}"  # pylint: disable=protected-access
        headers["X-Request-Id"] = uuid4().hex

        try:
            return self.do(method=method, url=self._url_make(section, dataset_id), **kwargs)
        except ResponseError as error:
            response = error.response
            error_code = response.json()["code"]
            raise ResponseErrorDistributor.get(error_code, ResponseError)(
                response=response
            ) from None


_T = TypeVar("_T")
_R = TypeVar("_R")


def multithread_upload(
    function: Callable[[_T], Optional[_R]],
    arguments: Iterable[_T],
    *,
    callback: Optional[Callable[[Tuple[_R, ...]], None]] = None,
    jobs: int = 1,
    pbar: Tqdm,
) -> None:
    """Multi-thread upload framework.

    Arguments:
        function: The upload function.
        arguments: The arguments of the upload function.
        callback: The callback function.
        jobs: The number of the max workers in multi-thread uploading procession.
        pbar: The :class:`Tqdm` instance for showing the upload process bar.

    """
    with ThreadPoolExecutor(jobs) as executor:
        if callback is not None:
            multi_callback = MultiCallbackTask(function=function, callback=callback)
            function = multi_callback.work
        futures = [executor.submit(function, argument) for argument in arguments]

        for future in futures:
            future.add_done_callback(pbar.update_callback)

        done, not_done = wait(futures, return_when=FIRST_EXCEPTION)

        if callback is not None:
            multi_callback.last_callback()

        for future in not_done:
            future.cancel()
        for future in done:
            future.result()


class MultiCallbackTask(Generic[_T, _R]):
    """A class for callbacking in multi-thread work.

    Arguments:
        function: The function of a single thread.
        callback: The callback function.
        size: The size of the task queue to send a callback.

    """

    def __init__(
        self,
        *,
        function: Callable[[_T], Optional[_R]],
        callback: Callable[[Tuple[_R, ...]], None],
        size: int = 50,
    ) -> None:
        self._lock = Lock()
        self._function = function
        self._callback = callback
        self._size = size
        self._arguments: Queue[_R] = Queue()  # pylint: disable=unsubscriptable-object

    def work(self, argument: _T) -> None:
        """Do the work of a single thread.

        Arguments:
            argument: The argument of the function.

        """
        callback_info = self._function(argument)
        if callback_info is not None:
            self._arguments.put(callback_info)
        with self._lock:
            if self._arguments.qsize() >= self._size:
                callback_arguments = tuple(self._arguments.get() for _ in range(self._size))
            else:
                callback_arguments = ()

        if callback_arguments:
            self._callback(callback_arguments)

    def last_callback(self) -> None:
        """Send the last callback when all works have been done."""
        callback_arguments = tuple(self._arguments.get() for _ in range(self._arguments.qsize()))
        if callback_arguments:
            self._callback(callback_arguments)
