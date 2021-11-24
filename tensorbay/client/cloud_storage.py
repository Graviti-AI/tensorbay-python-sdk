#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Related classes for the Storage Config."""

from typing import Any, Dict, Iterator, List, Type, TypeVar

from tensorbay.client.requests import Client
from tensorbay.dataset import AuthData
from tensorbay.utility import URL, AttrsMixin, ReprMixin, attr, camel, common_loads


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
            AuthData(
                cloud_path,
                url=URL.from_getter(
                    lambda c=cloud_path: self._get_url(c),
                    lambda c=cloud_path: self._get_url(c),  # type: ignore[misc]
                ),
            )
            for cloud_path in self._list_files(path)
        ]


class StorageConfig(AttrsMixin, ReprMixin):
    """This is a class stores the information of storage config.

    Arguments:
        name: The storage config name.
        file_path: Storage config path of the bucket.
        type_: Type of the storage provider, such as oss, s3, azure.
        is_graviti_storage: Whether the config is belong to graviti.

    """

    _T = TypeVar("_T", bound="StorageConfig")

    _repr_attrs = ("file_path", "type", "is_graviti_storage")

    name: str = attr()
    file_path: str = attr(key=camel)
    type: str = attr()
    is_graviti_storage: bool = attr(key=camel)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        file_path: str,
        type_: str,
        is_graviti_storage: bool,
    ) -> None:
        self.name = name
        self.file_path = file_path
        self.type = type_
        self.is_graviti_storage = is_graviti_storage

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`StorageConfig` instance from the given contents.

        Arguments:
            contents: The given dict containing the storage config::

                {
                    "name":                 <str>,
                    "filePath":             <str>,
                    "type":                 <str>,
                    "isGravitiStorage":     <boolean>
                }

        Returns:
            The loaded :class:`StorageConfig` instance.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the storage config into a dict.

        Returns:
            A dict containing all the information of the StorageConfig::

                {
                    "name":                 <str>,
                    "filePath":             <str>,
                    "type":                 <str>,
                    "isGravitiStorage":     <boolean>
                }

        """
        return self._dumps()
