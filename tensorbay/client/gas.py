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

import logging
from typing import Any, Dict, Generator, Optional, Type, Union, overload

from typing_extensions import Literal

from ..dataset import Dataset, FusionDataset
from ..exception import DatasetTypeError, ResourceNotExistError
from .dataset import DatasetClient, FusionDatasetClient
from .log import UPLOAD_DATASET_RESUME_TEMPLATE
from .requests import Client, PagingList, Tqdm

DatasetClientType = Union[DatasetClient, FusionDatasetClient]

logger = logging.getLogger(__name__)


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

    def _generate_auth_storage_configs(
        self, name: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Dict[str, Any], None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name

        response = self._client.open_api_do("GET", "auth-storage-configs", "", params=params).json()

        yield from response["configs"]

        return response["totalCount"]  # type: ignore[no-any-return]

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
            ResourceNotExistError: When the required dataset does not exist.

        """
        if not name:
            raise ResourceNotExistError(resource="dataset", identification=name)

        try:
            response = self._list_datasets(name=name)
            info = response["datasets"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="dataset", identification=name) from error

        return info  # type: ignore[no-any-return]

    def _list_datasets(
        self,
        name: Optional[str] = None,
        need_team_dataset: bool = False,  # personal: False, all: True
        offset: int = 0,
        limit: int = 128,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }
        if name:
            params["name"] = name
        if need_team_dataset:
            params["needTeamDataset"] = need_team_dataset

        response = self._client.open_api_do("GET", "", params=params)
        return response.json()  # type: ignore[no-any-return]

    def _generate_dataset_names(
        self,
        name: Optional[str] = None,
        need_team_dataset: bool = False,  # personal: False, all: True
        offset: int = 0,
        limit: int = 128,
    ) -> Generator[str, None, int]:
        response = self._list_datasets(name, need_team_dataset, offset, limit)

        for item in response["datasets"]:
            yield item["name"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def get_auth_storage_config(self, name: str) -> Dict[str, Any]:
        """Get the auth storage config with the given name.

        Arguments:
            name: The required auth storage config name.

        Returns:
            The auth storage config with the given name.

        Raises:
            TypeError: When the given auth storage config is illegal.
            ResourceNotExistError: When the required auth storage config does not exist.

        """
        if not name:
            raise TypeError("The given auth storage config name is illegal")

        try:
            config = next(self._generate_auth_storage_configs(name))
        except StopIteration as error:
            raise ResourceNotExistError(
                resource="auth storage config", identification=name
            ) from error

        return config

    def list_auth_storage_configs(self) -> PagingList[Dict[str, Any]]:
        """List auth storage configs.

        Returns:
            The PagingList of all auth storage configs.

        """
        return PagingList(
            lambda offset, limit: self._generate_auth_storage_configs(None, offset, limit),
            128,
        )

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

    def create_auth_dataset(
        self, name: str, config_name: str, path: str, is_fusion: bool = False
    ) -> DatasetClientType:
        """Create a TensorBay dataset with given name in auth cloud storage.

        The dataset will be linked to the given auth cloud storage
            and all of relative data will be stored in auth cloud storage.

        Arguments:
            name: Name of the dataset, unique for a user.
            config_name: The auth storage config name.
            path: The path of the dataset to create in auth cloud storage.
            is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.

        Returns:
            The created :class:`~tensorbay.client.dataset.DatasetClient` instance or
            :class:`~tensorbay.client.dataset.FusionDatasetClient` instance (is_fusion=True),
            and the status of dataset client is "commit".

        """
        post_data = {
            "name": name,
            "type": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
            "storageConfig": {"name": config_name, "path": path},
        }
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
            DatasetTypeError: When the requested dataset type is not the same as given.

        """
        info = self._get_dataset(name)

        dataset_id = info["id"]
        type_flag = info["type"]
        commit_id = info["HEAD"]["commitId"]

        if is_fusion != type_flag:
            raise DatasetTypeError(name, type_flag)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self, commit_id=commit_id)

    def list_dataset_names(self) -> PagingList[str]:
        """List names of all TensorBay datasets.

        Returns:
            The PagingList of all TensorBay dataset names.

        """
        return PagingList(
            lambda offset, limit: self._generate_dataset_names(None, False, offset, limit), 128
        )

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
        quiet: bool = False,
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
        quiet: bool = False,
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
        quiet: bool = False,
    ) -> DatasetClientType:
        ...

    def upload_dataset(
        self,
        dataset: Union[Dataset, FusionDataset],
        draft_number: Optional[int] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
        quiet: bool = False,
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
            quiet: Set to True to stop showing the upload process bar.

        Returns:
            The :class:`~tensorbay.client.dataset.DatasetClient` or
            :class:`~tensorbay.client.dataset.FusionDatasetClient`
            bound with the uploaded dataset.

        Raises:
            Exception: When Exception was raised during uploding dataset.

        """
        dataset_client = self.get_dataset(dataset.name, isinstance(dataset, FusionDataset))
        if draft_number:
            dataset_client.checkout(draft_number=draft_number)
        else:
            dataset_client.create_draft()

        try:
            if dataset.catalog:
                dataset_client.upload_catalog(dataset.catalog)

            dataset_client.update_notes(**dataset.notes)  # type: ignore[arg-type]

            with Tqdm(sum(len(segment) for segment in dataset), disable=quiet) as pbar:
                for segment in dataset:
                    dataset_client._upload_segment(  # pylint: disable=protected-access
                        segment,  # type: ignore[arg-type]
                        jobs=jobs,
                        skip_uploaded_files=skip_uploaded_files,
                        pbar=pbar,
                    )
        except Exception:
            logger.error(
                UPLOAD_DATASET_RESUME_TEMPLATE,
                dataset_client.status.draft_number,
                dataset_client.status.draft_number,
            )
            raise

        return dataset_client

    def delete_dataset(self, name: str) -> None:
        """Delete a TensorBay dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.

        """
        dataset_id = self._get_dataset(name)["id"]
        self._client.open_api_do("DELETE", "", dataset_id)
