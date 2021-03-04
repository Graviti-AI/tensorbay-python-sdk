#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class GAS.

The :class:`GAS` defines the initial client to interact between local and TensorBay.
It provides some operations on datasets level such as :meth:`GAS.create_dataset`,
:meth:`GAS.list_dataset_names` and :meth:`GAS.upload_dataset_object`.

AccessKey is required when operating with dataset.

"""

import sys
from typing import Any, Dict, Iterator, Optional, Tuple, Type, Union, overload

from typing_extensions import Literal

from ..dataset import Dataset, FusionDataset
from .dataset import DatasetClient, FusionDatasetClient
from .exceptions import GASDatasetError, GASDatasetTypeError
from .requests import Client, paging_range

DatasetClientType = Union[DatasetClient, FusionDatasetClient]


class GAS:
    """:class:`GAS` defines the initial client to interact between local and TensorBay.

    :class:`GAS` provides some operations on dataset level such as
    :meth:`GAS.create_dataset` :meth:`GAS.list_dataset_names` and :meth:`GAS.upload_dataset_object`.

    Arguments:
        access_key: User's access key.
        url: The host URL of the gas website.

    """

    _VERSIONS = {1: "COMMUNITY", 2: "ENTERPRISE"}

    def __init__(self, access_key: str, url: str = "") -> None:
        self._client = Client(access_key, url)

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[False],
        is_continuous: bool,
        region: Optional[str],
    ) -> DatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[True],
        is_continuous: bool,
        region: Optional[str],
    ) -> FusionDatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        is_continuous: bool = False,
        region: Optional[str] = None,
    ) -> DatasetClientType:
        ...

    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        is_continuous: bool = False,
        region: Optional[str] = None,  # beijing, hangzhou, shanghai
    ) -> DatasetClientType:
        """Create a TensorBay dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.
            is_fusion: Whether dataset is fusion, True for fusion dataset.
            is_continuous: Whether the data in dataset is continuous.
            region: Region of the dataset to be stored,
                only support "beijing", "hangzhou", "shanghai", default is "shanghai".

        Returns:
            The created :class:`~tensorbay.client.dataset.DatasetClient` or
                :class:`~tensorbay.client.dataset.FusionDatasetClient`(if is_fusion=True)

        """
        post_data = {
            "name": name,
            "type": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
            "isContinuous": is_continuous,
        }
        if region:
            post_data["region"] = region

        response = self._client.open_api_do("POST", "", json=post_data)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, response.json()["id"], self._client)

    def _get_dataset(self, name: str, commit_id: Optional[str] = None) -> DatasetClientType:
        dataset_id, is_fusion = self._get_dataset_id_and_type(name)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self._client, commit_id)

    def get_dataset(
        self, name: str, is_fusion: bool = False, commit_id: Optional[str] = None
    ) -> DatasetClientType:
        """Get a TensorBay dataset with given name and commit ID.

        Arguments:
            name: The name of the requested dataset.
            is_fusion: Whether dataset is fusion, True for fusion dataset.
            commit_id: The dataset commit ID.

        Returns:
            The requested :class:`~tensorbay.client.dataset.DatasetClient` or
                :class:`~tensorbay.client.dataset.FusionDatasetClient`(if is_fusion=True)

        Raises:
            GASDatasetTypeError: When the requested dataset is a fusion dataset.

        """
        client = self._get_dataset(name, commit_id)
        if not is_fusion:
            if not isinstance(client, DatasetClient):
                raise GASDatasetTypeError(name, True)
        else:
            if not isinstance(client, FusionDatasetClient):
                raise GASDatasetTypeError(name, False)

        return client

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

    def list_dataset_names(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List names of all TensorBay datasets.

        Arguments:
            start: The index to start.
            stop: The index to stop.

        Yields:
            Names of all datasets.

        """
        yield from (item["name"] for item in self._list_datasets(start=start, stop=stop))

    def _get_dataset_id_and_type(self, name: str) -> Tuple[str, bool]:
        """Get the ID and the type of the TensorBay dataset with the input name.

        Arguments:
            name: The name of the requested dataset.

        Returns:
            The tuple of dataset ID and type, True for fusion dataset.

        Raises:
            GASDatasetError: When the required dataset does not exist.

        """
        if not name:
            raise GASDatasetError(name)

        try:
            info = next(self._list_datasets(name))
        except StopIteration as error:
            raise GASDatasetError(name) from error

        return (
            info["id"],
            bool(info["type"]),
        )

    def rename_dataset(self, name: str, new_name: str) -> None:
        """Rename a TensorBay Dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.
            new_name: New name of the dataset, unique for a user.

        """
        dataset_id, _ = self._get_dataset_id_and_type(name)
        patch_data: Dict[str, str] = {"name": new_name}
        self._client.open_api_do("PATCH", "settings", dataset_id, json=patch_data)

    @overload
    def upload_dataset_object(
        self,
        dataset: Dataset,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClient:
        ...

    @overload
    def upload_dataset_object(
        self,
        dataset: FusionDataset,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionDatasetClient:
        ...

    @overload
    def upload_dataset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClientType:
        ...

    def upload_dataset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
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

        Returns:
            The :class:`~tensorbay.client.dataset.DatasetClient` or
                :class:`~tensorbay.client.dataset.FusionDatasetClient`
                bound with the uploaded dataset.

        """
        if isinstance(dataset, FusionDataset):
            dataset_client = self.get_dataset(dataset.name, is_fusion=True)
        else:
            dataset_client = self.get_dataset(dataset.name)

        if dataset.catalog:
            dataset_client.upload_catalog(dataset.catalog)

        for segment in dataset:
            dataset_client.upload_segment_object(
                segment,  # type: ignore[arg-type]
                jobs=jobs,
                skip_uploaded_files=skip_uploaded_files,
            )

        return dataset_client

    def delete_dataset(self, name: str) -> None:
        """Delete a dataset with given name.

        Arguments:
            name: Name of the :class:`~tensorbay.dataset.dataset.Dataset`, unique for a user.

        """
        dataset_id, _ = self._get_dataset_id_and_type(name)
        self._client.open_api_do("DELETE", "", dataset_id)
