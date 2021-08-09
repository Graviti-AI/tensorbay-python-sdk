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
from ..exception import DatasetTypeError, OperationError, ResourceNotExistError
from .cloud_storage import CloudClient
from .dataset import DatasetClient, FusionDatasetClient
from .lazy import PagingList
from .log import UPLOAD_DATASET_RESUME_TEMPLATE
from .requests import Client, Tqdm
from .status import Status
from .struct import ROOT_COMMIT_ID, UserInfo

DatasetClientType = Union[DatasetClient, FusionDatasetClient]

logger = logging.getLogger(__name__)

DEFAULT_BRANCH = "main"


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
        commit_id = info["commitId"]
        default_branch = info["defaultBranch"]
        dataset_alias = info["alias"]

        status = Status(default_branch, commit_id=commit_id)

        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self, status=status, alias=dataset_alias)

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

        dataset_id = info["id"]
        response = self._client.open_api_do("GET", "", dataset_id).json()
        response["id"] = dataset_id
        return response

    def _list_datasets(
        self,
        name: Optional[str] = None,
        offset: int = 0,
        limit: int = 128,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }
        if name:
            params["name"] = name

        response = self._client.open_api_do("GET", "", params=params)
        return response.json()  # type: ignore[no-any-return]

    def _generate_dataset_names(
        self,
        name: Optional[str] = None,
        offset: int = 0,
        limit: int = 128,
    ) -> Generator[str, None, int]:
        response = self._list_datasets(name, offset, limit)

        for item in response["datasets"]:
            yield item["name"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def get_user(self) -> UserInfo:
        """Get the user information with the current accesskey.

        Returns:
            The :class:`.struct.UserInfo` with the current accesskey.

        """
        response = self._client.open_api_do("GET", "users").json()
        return UserInfo.loads(response)

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

    def get_cloud_client(self, name: str) -> CloudClient:
        """Get a cloud client used for interacting with cloud platform.

        Arguments:
            name: The required auth storage config name.

        Returns:
            The cloud client of this dataset.
        """
        return CloudClient(name, self._client)

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[False] = False,
        *,
        region: Optional[str] = None,
        alias: str = "",
    ) -> DatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: Literal[True],
        *,
        region: Optional[str] = None,
        alias: str = "",
    ) -> FusionDatasetClient:
        ...

    @overload
    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        *,
        region: Optional[str] = None,
        alias: str = "",
    ) -> DatasetClientType:
        ...

    def create_dataset(
        self,
        name: str,
        is_fusion: bool = False,
        *,
        region: Optional[str] = None,  # beijing, hangzhou, shanghai
        alias: str = "",
    ) -> DatasetClientType:
        """Create a TensorBay dataset with given name.

        Arguments:
            name: Name of the dataset, unique for a user.
            is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.
            region: Region of the dataset to be stored,
                only support "beijing", "hangzhou", "shanghai", default is "shanghai".
            alias: Alias of the dataset, default is "".

        Returns:
            The created :class:`~tensorbay.client.dataset.DatasetClient` instance or
            :class:`~tensorbay.client.dataset.FusionDatasetClient` instance (is_fusion=True),
            and the status of dataset client is "commit".

        """
        post_data = {
            "name": name,
            "type": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
            "alias": alias,
        }
        if region:
            post_data["region"] = region

        status = Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID)

        response = self._client.open_api_do("POST", "", json=post_data)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, response.json()["id"], self, status=status, alias=alias)

    def create_auth_dataset(
        self,
        name: str,
        config_name: str,
        *,
        is_fusion: bool = False,
        alias: str = "",
    ) -> DatasetClientType:
        """Create a TensorBay dataset with given name in auth cloud storage.

        The dataset will be linked to the given auth cloud storage
            and all of relative data will be stored in auth cloud storage.

        Arguments:
            name: Name of the dataset, unique for a user.
            config_name: The auth storage config name.
            is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.
            alias: Alias of the dataset, default is "".

        Returns:
            The created :class:`~tensorbay.client.dataset.DatasetClient` instance or
            :class:`~tensorbay.client.dataset.FusionDatasetClient` instance (is_fusion=True),
            and the status of dataset client is "commit".

        """
        post_data = {
            "name": name,
            "type": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
            "configName": config_name,
            "alias": alias,
        }

        status = Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID)

        response = self._client.open_api_do("POST", "", json=post_data)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, response.json()["id"], self, status=status, alias=alias)

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
        commit_id = info["commitId"]
        default_branch = info["defaultBranch"]
        dataset_alias = info["alias"]

        status = Status(default_branch, commit_id=commit_id)

        if is_fusion != type_flag:
            raise DatasetTypeError(name, type_flag)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self, status=status, alias=dataset_alias)

    def list_dataset_names(self) -> PagingList[str]:
        """List names of all TensorBay datasets.

        Returns:
            The PagingList of all TensorBay dataset names.

        """
        return PagingList(
            lambda offset, limit: self._generate_dataset_names(None, offset, limit), 128
        )

    def update_dataset(self, name: str, *, alias: Optional[str] = None) -> None:
        """Update a TensorBay Dataset.

        Arguments:
            name: Name of the dataset, unique for a user.
            alias: New alias of the dataset.

        """
        dataset_id = self._get_dataset(name)["id"]
        patch_data = {}
        if alias is not None:
            patch_data["alias"] = alias

        if patch_data:
            self._client.open_api_do("PATCH", "", dataset_id, json=patch_data)

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
        branch_name: Optional[str] = None,
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
        branch_name: Optional[str] = None,
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
        branch_name: Optional[str] = None,
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
        branch_name: Optional[str] = None,
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
            draft_number: The draft number.
            branch_name: The branch name.
            jobs: The number of the max workers in multi-thread upload.
            skip_uploaded_files: Set it to True to skip the uploaded files.
            quiet: Set to True to stop showing the upload process bar.

        Returns:
            The :class:`~tensorbay.client.dataset.DatasetClient` or
            :class:`~tensorbay.client.dataset.FusionDatasetClient`
            bound with the uploaded dataset.

        Raises:
            OperationError: When uploading the dataset based on both draft number
                and branch name is not allowed.
            Exception: When Exception was raised during uploading dataset.

        """
        dataset_client = self.get_dataset(dataset.name, isinstance(dataset, FusionDataset))

        if draft_number and branch_name:
            raise OperationError(
                "Uploading the dataset based on both draft number and branch name is not allowed"
            )

        if draft_number:
            dataset_client.checkout(draft_number=draft_number)

        else:
            target_branch_name = branch_name if branch_name else dataset_client.status.branch_name

            for draft in dataset_client.list_drafts():
                if draft.branch_name == target_branch_name:
                    dataset_client.checkout(draft_number=draft.number)
                    break
            else:
                dataset_client.create_draft(
                    'Draft autogenerated by "GAS.upload_dataset"', branch_name=target_branch_name
                )

        try:
            if dataset.catalog:
                dataset_client.upload_catalog(dataset.catalog)

            dataset_client.update_notes(**dataset.notes)  # type: ignore[arg-type]

            if isinstance(dataset, Dataset):
                data_count = sum(len(segment) for segment in dataset)
            else:
                data_count = sum(
                    sum(len(frame) for frame in fusion_segment) for fusion_segment in dataset
                )

            with Tqdm(data_count, disable=quiet) as pbar:
                for segment in dataset:
                    dataset_client._upload_segment(  # pylint: disable=protected-access
                        segment,  # type: ignore[arg-type]
                        jobs=jobs,
                        skip_uploaded_files=skip_uploaded_files,
                        pbar=pbar,
                    )
        except Exception:
            if draft_number:
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
