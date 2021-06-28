#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class CloudClient.

The :class:`CloudClient` defines the initial client to interact between local and cloud platform.

"""

from http.client import HTTPResponse
from typing import Any, Dict, Iterator, List

from .requests import Client


class CloudClient:
    """:class:`CloudClient` defines the client to interact between local and cloud platform.

    Arguments:
        name: Name of the auth cloud storage config.
        client: The initial client to interact between local and TensorBay.

    """

    def __init__(self, name: str, client: Client) -> None:
        self._name = name
        self._client = client

    def _make_section(self, section: str) -> str:
        return f"cloud/{self._name}/{section}"

    def _list_files(self, path: str, limit: int = 128) -> Iterator[str]:
        params: Dict[str, Any] = {"prefix": path, "limit": limit}

        while True:
            response = self._client.open_api_do(
                "GET", self._make_section("files"), params=params
            ).json()
            yield from response["cloudFiles"]

            if not response["truncated"]:
                break
            params["marker"] = response["nextMarker"]

    def list_files(self, path: str) -> List[str]:
        """List all cloud files in the given directory.

        Arguments:
            path: The directory path on the cloud platform.

        Returns:
            The list of all the cloud files.

        """
        return list(self._list_files(path))

    def open(self, file_path: str) -> HTTPResponse:
        """Return the binary file pointer of this file.

        Arguments:
            file_path: The path of the file on the cloud platform.

        Returns: #noqa: DAR202
            The cloud file pointer of this file path.

        """
