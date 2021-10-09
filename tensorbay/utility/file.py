#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""mixin classes for local file and remote file."""

import os
from hashlib import sha1
from http.client import HTTPResponse
from string import printable
from typing import Any, Callable, Dict, Optional, Union
from urllib.error import URLError
from urllib.parse import quote, urljoin
from urllib.request import pathname2url, urlopen

from _io import BufferedReader

from tensorbay.utility.repr import ReprMixin


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
        _url_getter: The url getter of the remote file.
        cache_path: The path to store the cache.

    Attributes:
        path: The file local path.

    """

    _repr_maxlevel = 3

    def __init__(
        self,
        remote_path: str,
        *,
        _url_getter: Optional[Callable[[str], str]] = None,
        _url_updater: Optional[Callable[[], None]] = None,
        cache_path: str = "",
    ) -> None:
        self.path = remote_path
        self._url_getter = _url_getter
        self._url_updater = _url_updater
        self.cache_path = os.path.join(cache_path, remote_path) if cache_path else ""

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

    def _urlopen(self) -> HTTPResponse:
        try:
            return urlopen(  # type: ignore[no-any-return]
                quote(self.get_url(), safe=printable), timeout=2
            )
        except URLError as error:
            if str(error) == "<urlopen error timed out>":
                self.update_url()
                return urlopen(quote(self.get_url(), safe=printable))  # type: ignore[no-any-return]
            raise

    def update_url(self) -> None:
        """Update the url when the url is timed out.

        Raises:
            ValueError: When the _url_updater is missing.

        """
        if not self._url_updater:
            raise ValueError(
                f"The file URL cannot be updated because {self._repr_head()} has no url updater"
            )

        self._url_updater()

    def get_url(self) -> str:
        """Return the url of the data hosted by tensorbay.

        Returns:
            The url of the data.

        Raises:
            ValueError: When the _url_getter is missing.

        """
        if not self._url_getter:
            raise ValueError(
                f"The file URL cannot be got because {self._repr_head()} has no url getter"
            )

        return self._url_getter(self.path)

    def open(self) -> Union[HTTPResponse, BufferedReader]:
        """Return the binary file pointer of this file.

        The remote file pointer will be obtained by ``urllib.request.urlopen()``.

        Returns:
            The remote file pointer for this data.

        """
        cache_path = self.cache_path
        if not cache_path:
            return self._urlopen()

        if not os.path.exists(cache_path):
            dirname = os.path.dirname(cache_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with self._urlopen() as fp:
                with open(cache_path, "wb") as cache:
                    cache.write(fp.read())

        return open(cache_path, "rb")
