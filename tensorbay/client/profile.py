#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Record statistics of the interface that interacts with TensorBay."""

import csv
import json
import math
import time
from collections import OrderedDict, defaultdict
from functools import wraps
from itertools import chain
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from types import MethodType
from typing import Any, Callable, DefaultDict, Dict, Optional, TypeVar
from urllib.parse import urlparse

from requests.models import Response
from requests_toolbelt.multipart.encoder import FileWrapper, MultipartEncoder

from tensorbay.client.requests import Client
from tensorbay.utility import RemoteFileMixin, UserResponse

_Callable = TypeVar("_Callable", bound=Callable[..., Response])
_OpenCallable = TypeVar("_OpenCallable", bound=Callable[..., UserResponse])
_ReadCallable = Callable[..., bytes]

_COLUMNS = OrderedDict(
    totalTime="{:<20.3f}",
    callNumber="{:<20}",
    avgTime="{:<20.3f}",
    totalResponseLength="{:<20}",
    totalFileSize="{:<13}",
    speed="{:<13}",
)
_TITLE = f"{'totalTime (s)':<20}{' |callNumber':<18}\
    {' |avgTime (s)':<22}{' |totalResponseLength':<22}{' |totalFileSize':<15}{' |speed':<15}"
_PATH_PREFIX = "/gatewayv2/tensorbay-open-api/v1/"
_UNITS = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def format_size(size: float) -> str:
    """Format a byte count as a human readable file size.

    Arguments:
        size: The size to format in bytes.

    Returns:
        The human readable string.

    """
    if size == 0:
        return "0B"

    index = int(math.log(size, 1024))
    number = pow(1024, index)
    return f"{size/number:.2f}{_UNITS[index]}"


class Profile:
    """This is a class used to save statistical summary."""

    _manager: SyncManager
    _summary: Dict[str, DefaultDict[str, Any]]

    def __init__(self) -> None:
        self.do_function = Client.do
        self.urlopen = RemoteFileMixin._urlopen

    def __enter__(self) -> "Profile":
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def _calculate_and_format(self) -> None:
        for key, value in self._summary.items():
            value["avgTime"] = value["totalTime"] / value["callNumber"]
            value["totalFileSize"] = format_size(value["rawTotalFileSize"])
            value["speed"] = f'{format_size(value["rawTotalFileSize"] / value["totalTime"])}/s'
            self._summary[key] = value

    @staticmethod
    def _format_string(path: str = "Path", item: Optional[Dict[str, float]] = None) -> str:
        content = [f"|{path:<63}"]
        if item is None:
            content.append(_TITLE)
        else:
            content.extend(value.format(item[key]) for key, value in _COLUMNS.items())
        content.append("\n")
        return " |".join(content)

    @staticmethod
    def _get_file_size(data: MultipartEncoder) -> int:
        for part in data.parts:
            body = part.body
            if isinstance(body, FileWrapper):
                return body.len  # type: ignore[no-any-return]

        return 0

    def _save_to_txt(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(self._format_string())
            for url, item in self._summary.items():
                fp.write(self._format_string(url, item))

    def _save_to_csv(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow(chain(["Path"], _COLUMNS.keys()))
            for post, item in self._summary.items():
                writer.writerow(chain([post], (item[key] for key in _COLUMNS)))

    def _save_to_json(self, path: str) -> None:
        summary = self._summary if isinstance(self._summary, dict) else self._summary.copy()
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(summary, fp, indent=4)

    def _statistical(self, func: _Callable) -> _Callable:
        """A decorator to record the running time, response length ..etc of the function.

        Arguments:
            func: The Client.do() function.

        Returns:
            The wrapped function.

        """

        @wraps(func)
        def wrapper(method: str, url: str, **kwargs: Any) -> Response:
            path = urlparse(url).path
            part = path.replace(_PATH_PREFIX, "") if path else url
            key = f"[{method}] {part}"
            data = kwargs.get("data")
            file_size = self._get_file_size(data) if isinstance(data, MultipartEncoder) else 0
            response = func(method, url, **kwargs)
            self._update(key, len(response.content), response.elapsed.total_seconds(), file_size)

            return response

        return wrapper  # type: ignore[return-value]

    def _statistical_read(self, download_path: str) -> _ReadCallable:
        def wrapper(response: UserResponse, amt: Optional[int] = None) -> bytes:
            start_time = time.time()
            content = UserResponse.read(response, amt)
            self._update(download_path, 0, time.time() - start_time, len(content))
            return content

        return wrapper

    def _statistical_open(self, func: _OpenCallable) -> _OpenCallable:
        @wraps(func)
        def wrapper(obj: RemoteFileMixin) -> UserResponse:
            netloc = urlparse(obj.url.get()).netloc  # type: ignore[union-attr]
            download_path = f"[GET] {netloc}/*"

            start_time = time.time()
            fp = func(obj)
            cost_time = time.time() - start_time

            item = self._summary.get(download_path, defaultdict(int))
            item["totalTime"] += cost_time
            self._summary[download_path] = item
            setattr(fp, "read", MethodType(self._statistical_read(download_path), fp))
            return fp

        return wrapper  # type: ignore[return-value]

    def _update(self, key: str, response_length: int, cost_time: float, file_size: int) -> None:
        """Update the giving information into summary.

        Arguments:
            key: the post method and url.
            response_length: response length of the post.
            cost_time: cost time of the post.
            file_size: the upload file size.

        """
        item = self._summary.get(key, defaultdict(int))
        item["totalTime"] += cost_time
        item["callNumber"] += 1
        item["totalResponseLength"] += response_length
        item["rawTotalFileSize"] += file_size
        self._summary[key] = item

    def save(self, path: str, file_type: str = "txt") -> None:
        """Save the statistical summary into a file.

        Arguments:
            path: The file local path.
            file_type: Type of the save file, only support 'txt', 'json', 'csv'.

        """
        self._calculate_and_format()
        writers = {"txt": self._save_to_txt, "json": self._save_to_json, "csv": self._save_to_csv}
        writers[file_type](path)

    def start(self, multiprocess: bool = False) -> None:
        """Start statistical record.

        Arguments:
            multiprocess: Whether the records is in a multi-process environment.

        """
        if multiprocess:
            self._manager = Manager()
            self._summary = self._manager.dict()
        else:
            self._summary = {}
        setattr(Client, "do", staticmethod(self._statistical(self.do_function)))
        setattr(RemoteFileMixin, "_urlopen", self._statistical_open(self.urlopen))

    def stop(self) -> None:
        """Stop statistical record."""
        setattr(Client, "do", self.do_function)
        setattr(RemoteFileMixin, "_urlopen", self.urlopen)
        if hasattr(self, "_manager"):
            self._summary = self._summary.copy()
            self._manager.shutdown()
            delattr(self, "_manager")


profile = Profile()
