#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""mixin classes for local file and remote file."""

import os
from hashlib import sha1
from http.client import HTTPResponse
from string import printable
from typing import Any, Callable, Dict, Optional
from urllib.parse import quote, urljoin
from urllib.request import pathname2url, urlopen

from _io import BufferedReader

from .repr import ReprMixin


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

    Attributes:
        path: The file local path.

    """

    _repr_maxlevel = 3

    def __init__(
        self, remote_path: str, *, _url_getter: Optional[Callable[[str], str]] = None
    ) -> None:
        self.path = remote_path
        self._url_getter = _url_getter

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

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

    def open(self) -> HTTPResponse:
        """Return the binary file pointer of this file.

        The remote file pointer will be obtained by ``urllib.request.urlopen()``.

        Returns:
            The remote file pointer for this data.

        """
        return urlopen(quote(self.get_url(), safe=printable))  # type: ignore[no-any-return]
