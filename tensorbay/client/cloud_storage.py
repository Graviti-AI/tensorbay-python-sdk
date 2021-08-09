#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class CloudClient.

The :class:`CloudClient` defines the initial client to interact between local and cloud platform.

"""

from typing import Any, Dict, Iterator, List

from ..dataset import AuthData
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

    def _get_url(self, file_path: str) -> str:
        params: Dict[str, Any] = {"filePath": file_path}

        response = self._client.open_api_do("GET", self._make_section("files/urls"), params=params)
        return response.json()["url"]  # type: ignore[no-any-return]

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

    def list_auth_data(self, path: str = "") -> List[AuthData]:
        """List all cloud files in the given directory as :class:`~tensorbay.dataset.data.AuthData`.

        Arguments:
            path: The directory path on the cloud platform.

        Returns:
            The list of :class:`~tensorbay.dataset.data.AuthData` of all the cloud files.

        """
        return [
            AuthData(cloud_path, _url_getter=self._get_url) for cloud_path in self._list_files(path)
        ]
