#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class GAS.

The :class:`GAS` defines the initial client to interact between local and TensorBay.
It provides some operations on datasets level such as :meth:`GAS.create_dataset`,
:meth:`GAS.list_dataset_names` and :meth:`GAS.get_dataset`.

AccessKey is required when operating with dataset.

"""

import sys
from typing import Any, Dict, Iterator, Optional, Type, Union, overload

from typing_extensions import Literal

from ..dataset import Dataset, FusionDataset
from .dataset import DatasetClient, FusionDatasetClient
from .exceptions import GASDatasetError, GASDatasetTypeError
from .requests import Client, paging_range

DatasetClientType = Union[DatasetClient, FusionDatasetClient]


class GAS:
    """:class:`GAS` defines the initial client to interact between local and TensorBay.

    :class:`GAS` provides some operations on dataset level such as
    :meth:`GAS.create_dataset` :meth:`GAS.list_dataset_names` and :meth:`GAS.get_dataset`.

    Arguments:
        access_key: User's access key.
        url: The host URL of the gas website.

    """

    def __init__(self, access_key: str, url: str = "") -> None:
        self._client = Client(access_key, url)

    def _get_dataset_with_any_type(self, name: str) -> DatasetClientType:
        info = self._get_dataset(name)
        dataset_id = info["id"]
        is_fusion = info["type"]
        commit_id = info["HEAD"]["commitId"]
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self, commit_id=commit_id)

    def _get_dataset(self, name: str) -> Dict[str, Any]:
        """Get the information of the TensorBay dataset with the input name.

        Arguments:
            name: The name of the requested dataset.

        Returns:
            The dict of dataset information.

        Raises:
            GASDatasetError: When the required dataset does not exist.

        """
        if not name:
            raise GASDatasetError(name)

        try:
            info = next(self._list_datasets(name))
        except StopIteration as error:
            raise GASDatasetError(name) from error

        return info

    def _list_datasets(
        self,
        name: Optional[str] = None,
        need_team_dataset: bool = False,  # personal: False, all: True
        *,
        start: int = 0,
        stop: int = sys.maxsize,
        page_size: int = 128,
    ) -> Iterator[Dict[str, Any]]:

        params: Dict[str, Any] = {}
        if name:
            params["name"] = name
        if need_team_dataset:
            params["needTeamDataset"] = need_team_dataset

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do("GET", "", params=params).json()
            yield from response["datasets"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[False] = False,
        *,
        region: Optional[str] = None,
    ) -> DatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[True],
        *,
        region: Optional[str] = None,
    ) -> FusionDatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        *,
        region: Optional[str] = None,
    ) -> DatasetClientType:
        ...

    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        *,
        region: Optional[str] = None,  # beijing, hangzhou, shanghai
    ) -> DatasetClientType:
        """Create a TensorBay dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.
            is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.
            region: Region of the dataset to be stored,
                only support "beijing", "hangzhou", "shanghai", default is "shanghai".

        Returns:
            The created :class:`~tensorbay.client.dataset.DatasetClient` instance or
                :class:`~tensorbay.client.dataset.FusionDatasetClient` instance (is_fusion=True),
                and the status of dataset client is "commit".

        """
        post_data = {
            "name": name,
            "type": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
        }
        if region:
            post_data["region"] = region

        response = self._client.open_api_do("POST", "", json=post_data)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, response.json()["id"], self)

    @overload
    def get_dataset(self, name: str, is_fusion: Literal[False] = False) -> DatasetClient:
        ...

    @overload
    def get_dataset(self, name: str, is_fusion: Literal[True]) -> FusionDatasetClient:
        ...

    @overload
    def get_dataset(self, name: str, is_fusion: bool = False) -> DatasetClientType:
        ...

    def get_dataset(self, name: str, is_fusion: bool = False) -> DatasetClientType:
        """Get a TensorBay dataset with given name and commit ID.

        Arguments:
            name: The name of the requested dataset.
            is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.

        Returns:
            The requested :class:`~tensorbay.client.dataset.DatasetClient` instance or
                :class:`~tensorbay.client.dataset.FusionDatasetClient` instance (is_fusion=True),
                and the status of dataset client is "commit".

        Raises:
            GASDatasetTypeError: When the requested dataset type is not the same as given.

        """
        info = self._get_dataset(name)

        dataset_id = info["id"]
        type_flag = info["type"]
        commit_id = info["HEAD"]["commitId"]

        if is_fusion != type_flag:
            raise GASDatasetTypeError(name, type_flag)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self, commit_id=commit_id)

    def list_dataset_names(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List names of all TensorBay datasets.

        Arguments:
            start: The index to start.
            stop: The index to stop.

        Yields:
            Names of all datasets.

        """
        yield from (item["name"] for item in self._list_datasets(start=start, stop=stop))

    def rename_dataset(self, name: str, new_name: str) -> None:
        """Rename a TensorBay Dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.
            new_name: New name of the dataset, unique for a user.

        """
        dataset_id = self._get_dataset(name)["id"]
        patch_data: Dict[str, str] = {"name": new_name}
        self._client.open_api_do("PATCH", "", dataset_id, json=patch_data)

    @overload
    def upload_dataset(
        self,
        dataset: Dataset,
        draft_number: Optional[int] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClient:
        ...

    @overload
    def upload_dataset(
        self,
        dataset: FusionDataset,
        draft_number: Optional[int] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionDatasetClient:
        ...

    @overload
    def upload_dataset(
        self,
        dataset: Union[Dataset, FusionDataset],
        draft_number: Optional[int] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClientType:
        ...

    def upload_dataset(
        self,
        dataset: Union[Dataset, FusionDataset],
        draft_number: Optional[int] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClientType:
        """Upload a local dataset to TensorBay.

        This function will upload all information contains
        in the :class:`~tensorbay.dataset.dataset.Dataset`
        or :class:`~tensorbay.dataset.dataset.FusionDataset`, which includes:

            - Create a TensorBay dataset with the name and type of input local dataset.
            - Upload all :class:`~tensorbay.dataset.segment.Segment`
                or :class:`~tensorbay.dataset.segment.FusionSegment` in the dataset to TensorBay.

        Arguments:
            dataset: The :class:`~tensorbay.dataset.dataset.Dataset` or
                :class:`~tensorbay.dataset.dataset. FusionDataset` needs to be uploaded.
            jobs: The number of the max workers in multi-thread upload.
            skip_uploaded_files: Set it to True to skip the uploaded files.
            draft_number: The draft number.

        Returns:
            The :class:`~tensorbay.client.dataset.DatasetClient` or
                :class:`~tensorbay.client.dataset.FusionDatasetClient`
                bound with the uploaded dataset.

        """
        dataset_client = self.get_dataset(dataset.name, isinstance(dataset, FusionDataset))
        if draft_number:
            dataset_client.checkout(draft_number=draft_number)
        else:
            dataset_client.create_draft()

        if dataset.catalog:
            dataset_client.upload_catalog(dataset.catalog)

        dataset_client.update_notes(**dataset.notes)  # type: ignore[arg-type]

        for segment in dataset:
            dataset_client.upload_segment(
                segment,  # type: ignore[arg-type]
                jobs=jobs,
                skip_uploaded_files=skip_uploaded_files,
            )

        return dataset_client

    def delete_dataset(self, name: str) -> None:
        """Delete a TensorBay dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.

        """
        dataset_id = self._get_dataset(name)["id"]
        self._client.open_api_do("DELETE", "", dataset_id)
