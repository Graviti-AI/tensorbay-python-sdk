#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Basic concepts of local file and remote file."""

import os
from hashlib import sha1
from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import urljoin
from urllib.request import pathname2url

from _io import BufferedReader

from tensorbay.exception import ResponseError
from tensorbay.utility.repr import ReprMixin
from tensorbay.utility.requests import UserResponse, config, get_session


class URL:
    """URL is a class used to get and update the url.

    Arguments:
        url: The url.
        updater: A function used to update the url.

    """

    def __init__(self, url: str, updater: Callable[[], Optional[str]]) -> None:
        self._updater = updater
        self._getter: Callable[..., str] = lambda: url

    @classmethod
    def from_getter(cls, getter: Callable[..., str], updater: Callable[[], Optional[str]]) -> "URL":
        """Create a URL instance from the given getter and updater.

        Arguments:
            getter: The url getter of the file.
            updater: The updater of the url.

        Returns:
            The URL instance which stores the url and the updater.

        """
        obj: "URL" = object.__new__(cls)
        obj._getter = getter
        obj._updater = updater
        return obj

    def update(self) -> None:
        """Update the url."""
        url = self._updater()
        if url is not None:
            self._getter = lambda: url  # type: ignore[assignment, return-value]

    def get(self) -> str:
        """Get the url of the file.

        Returns:
            The url.

        """
        return self._getter()


class FileMixin(ReprMixin):
    """FileMixin is a mixin class to mixin file related methods for local file.

    Arguments:
        local_path: The file local path.

    Attributes:
        path: The file local path.

    """

    _checksum: str

    _repr_maxlevel = 3
    _BUFFER_SIZE = 65536

    def __init__(self, local_path: str) -> None:
        self.path = local_path

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

    def _get_callback_body(self) -> Dict[str, Any]:
        return {"checksum": self.get_checksum(), "fileSize": os.path.getsize(self.path)}

    def get_checksum(self) -> str:
        """Get and cache the sha1 checksum of the local data.

        Returns:
            The sha1 checksum of the local data.

        """
        if not hasattr(self, "_checksum"):
            sha1_object = sha1()
            with open(self.path, "rb") as fp:
                while True:
                    data = fp.read(self._BUFFER_SIZE)
                    if not data:
                        break
                    sha1_object.update(data)

            self._checksum = sha1_object.hexdigest()

        return self._checksum

    def get_url(self) -> str:
        """Return the url of the local data file.

        Returns:
            The url of the local data.

        """
        return urljoin("file:", pathname2url(os.path.abspath(self.path)))

    def open(self) -> BufferedReader:
        """Return the binary file pointer of this file.

        The local file pointer will be obtained by build-in ``open()``.

        Returns:
            The local file pointer for this data.

        """
        return open(self.path, "rb")


class RemoteFileMixin(ReprMixin):
    """RemoteFileMixin is a mixin class to mixin file related methods for remote file.

    Arguments:
        local_path: The file local path.
        url: The URL instance used to get and update url.
        cache_path: The path to store the cache.

    Attributes:
        path: The file local path.

    """

    _repr_maxlevel = 3

    def __init__(
        self,
        remote_path: str,
        *,
        url: Optional[URL] = None,
        cache_path: str = "",
    ) -> None:
        self.path = remote_path
        self.url = url
        self.cache_path = os.path.join(cache_path, remote_path) if cache_path else ""

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

    def _urlopen(self) -> UserResponse:

        if not self.url:
            raise ValueError(f"The file cannot open because {self._repr_head()} has no url")

        try:
            session = get_session()
            return UserResponse(
                session.request("GET", self.get_url(), timeout=config.timeout, stream=True)
            )
        except ResponseError as error:
            if error.response.status_code == 403:
                self.url.update()
                return UserResponse(
                    get_session().request(
                        "GET", self.get_url(), timeout=config.timeout, stream=True
                    )
                )
            raise

    def _write_cache(self, cache_path: str) -> None:
        dirname = os.path.dirname(cache_path)
        os.makedirs(dirname, exist_ok=True)
        temp_path = f"{cache_path}.tensorbay.downloading.{os.getpid()}"
        with self._urlopen() as fp:
            with open(temp_path, "wb") as cache:
                cache.write(fp.read())
        os.rename(temp_path, cache_path)

    def get_url(self) -> str:
        """Return the url of the data hosted by tensorbay.

        Returns:
            The url of the data.

        Raises:
            ValueError: When the url is missing.

        """
        if not self.url:
            raise ValueError(f"The file URL cannot be got because {self._repr_head()} has no url")

        return self.url.get()

    def open(self) -> Union[UserResponse, BufferedReader]:
        """Return the binary file pointer of this file.

        The remote file pointer will be obtained by ``urllib.request.urlopen()``.

        Returns:
            The remote file pointer for this data.

        """
        cache_path = self.cache_path
        if not cache_path:
            return self._urlopen()

        if not os.path.exists(cache_path):
            self._write_cache(cache_path)

        return open(cache_path, "rb")
