#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Statistical.

:class:`Profile` is a class used to save statistical summary.

"""

import json
import time
from collections import defaultdict
from functools import wraps
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from typing import Any, Callable, DefaultDict, Dict, TypeVar

from requests.models import Response

from .requests import Client

_Callable = TypeVar("_Callable", bound=Callable[..., Response])


class Profile:
    """This is a class used to save statistical summary."""

    _manager: SyncManager
    _summary: Dict[str, DefaultDict[str, Any]]

    def __init__(self) -> None:
        self.do_function = Client.do

    def __enter__(self) -> "Profile":
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def _calculate_average_time(self) -> None:
        for key, value in self._summary.items():
            value["avgTime"] = value["totalTime"] / value["callNumber"]
            self._summary[key] = value

    def statistical(self, func: _Callable) -> _Callable:
        """A decorator to record the running time, response length ..etc of the function.

        Arguments:
            func: The Client.do() function.

        Returns:
            The wrapped function.

        """

        @wraps(func)
        def wrapper(client: Client, method: str, url: str, **kwargs: Any) -> Response:
            key = f"[{method}] {url}"
            data_length = getattr(kwargs.get("data"), "len", 0)
            start_time = time.time()
            response = func(client, method, url, **kwargs)
            cost_time = time.time() - start_time
            self.update(key, len(response.content), cost_time, data_length)

            return response

        return wrapper  # type: ignore[return-value]

    def update(self, key: str, response_length: int, cost_time: float, file_size: int) -> None:
        """Update the giving information into summary.

        Arguments:
            key: the post method and url.
            response_length: response length of the post.
            cost_time: cost time of the post.
            file_size: the upload file size.

        """
        item = self._summary.get(key, defaultdict(float))
        item["totalTime"] += cost_time
        item["callNumber"] += 1
        item["totalResponseLength"] += response_length
        item["totalFileSize"] += file_size
        self._summary[key] = item

    def save(self, path: str) -> None:
        """Save the statistical summary into a file.

        Arguments:
            path: The file local path.

        """
        self._calculate_average_time()
        summary = self._summary if isinstance(self._summary, dict) else self._summary.copy()
        with open(path, "w") as fp:
            json.dump(summary, fp, indent=4)

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

        Client.do = self.statistical(self.do_function)  # type: ignore[assignment]

    def stop(self) -> None:
        """Stop statistical record."""
        Client.do = self.do_function  # type: ignore[assignment]
        delattr(self, "_summary")
        if hasattr(self, "_manager"):
            self._manager.shutdown()
            delattr(self, "_manager")


profile = Profile()
