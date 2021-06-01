#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...exception import DatasetTypeError, ResourceNotExistError
from .. import gas
from ..dataset import DatasetClient, FusionDatasetClient
from ..gas import GAS
from ..requests import PagingList
from .utility import mock_response


class TestGAS:
    gas_client = GAS("Accesskey-********************************")

    def test_generate_auth_storage_configs(self, mocker):
        params = {"name": "cloud_config", "offset": 0, "limit": 128}
        json_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                }
            ],
            "totalCount": 1,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data=json_data),
        )
        assert (
            next(self.gas_client._generate_auth_storage_configs("cloud_config"))
            == json_data["configs"][0]
        )

        open_api_do.assert_called_once_with("GET", "auth-storage-configs", "", params=params)

    @pytest.mark.parametrize("type_", [0, 1])
    def test_get_dataset_with_any_type(self, mocker, type_):
        get_dataset = mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={"id": "123456", "type": type_, "commitId": "4"},
        )
        dataset_client = self.gas_client._get_dataset_with_any_type("test")
        dataset_type = FusionDatasetClient if type_ else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == "test"
        assert dataset_client._dataset_id == "123456"
        assert dataset_client._status.commit_id == "4"
        get_dataset.assert_called_once_with("test")

    def test_get_dataset_(self, mocker):
        with pytest.raises(ResourceNotExistError):
            self.gas_client._get_dataset("")
        mocker.patch(
            f"{gas.__name__}.GAS._list_datasets",
            return_value={"datasets": []},
        )
        with pytest.raises(ResourceNotExistError):
            self.gas_client._get_dataset("test")

        json_data = {
            "datasets": [
                {
                    "id": "12345",
                    "name": "test",
                    "type": 0,
                }
            ],
        }
        mocker.patch(
            f"{gas.__name__}.GAS._list_datasets",
            return_value=json_data,
        )
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data={"id": "54321"}),
        )
        assert self.gas_client._get_dataset("test") == {"id": "12345"}
        open_api_do.assert_called_once_with("GET", "", "12345")

    def test_list_datasets(self, mocker):
        params = {
            "name": "test",
            "offset": 0,
            "limit": 128,
        }
        json_data = {
            "datasets": [
                {
                    "id": "12345",
                    "name": "test",
                    "type": 0,
                }
            ],
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data=json_data),
        )
        assert self.gas_client._list_datasets("test") == json_data
        open_api_do.assert_called_once_with("GET", "", params=params)

    def test_get_auth_storage_config(self, mocker):
        with pytest.raises(TypeError):
            self.gas_client.get_auth_storage_config("")

        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data={"configs": [], "totalCount": 0}),
        )
        with pytest.raises(ResourceNotExistError):
            self.gas_client.get_auth_storage_config("cloud_config")

        json_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                }
            ],
            "totalCount": 1,
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data=json_data),
        )
        assert self.gas_client.get_auth_storage_config("cloud_config") == json_data["configs"][0]

    def test_list_auth_storage_configs(self, mocker):
        json_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                }
            ],
            "totalCount": 1,
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data=json_data),
        )
        configs = self.gas_client.list_auth_storage_configs()

        assert len(configs) == 1

    @pytest.mark.parametrize("is_fusion", [True, False])
    def test_create_dataset(self, mocker, is_fusion):
        params = {"name": "test", "type": int(is_fusion), "region": "beijing"}
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data={"id": "12345"}),
        )
        dataset_client = self.gas_client.create_dataset("test", is_fusion, region="beijing")
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == "test"
        assert dataset_client._dataset_id == "12345"
        open_api_do.assert_called_once_with("POST", "", json=params)

    @pytest.mark.parametrize("is_fusion", [True, False])
    def test_create_auth_dataset(self, mocker, is_fusion):
        params = {
            "name": "test",
            "type": int(is_fusion),
            "storageConfig": {"name": "cloud_config", "path": "path/to/dataset"},
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(json_data={"id": "12345"}),
        )
        dataset_client = self.gas_client.create_auth_dataset(
            "test", "cloud_config", "path/to/dataset", is_fusion
        )
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == "test"
        assert dataset_client._dataset_id == "12345"
        open_api_do.assert_called_once_with("POST", "", json=params)

    @pytest.mark.parametrize("is_fusion", [True, False])
    def test_get_dataset(self, mocker, is_fusion):
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={"id": "123456", "type": 1, "commitId": "4"},
        )
        with pytest.raises(DatasetTypeError):
            self.gas_client.get_dataset("test")

        get_dataset = mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={"id": "123456", "type": int(is_fusion), "commitId": "4"},
        )
        dataset_client = self.gas_client.get_dataset("test", is_fusion)
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == "test"
        assert dataset_client._dataset_id == "123456"
        assert dataset_client._status.commit_id == "4"
        get_dataset.assert_called_once_with("test")

    def test_list_dataset_names(self, mocker):
        paging_list = mocker.patch(f"{gas.__name__}.PagingList")
        self.gas_client.list_dataset_names()
        paging_list.assert_called()

    def test_rename_dataset(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={"id": "123456", "type": 1, "commitId": "4"},
        )
        patch_data = {"name": "new_test"}
        self.gas_client.rename_dataset("test", "new_test")
        open_api_do.assert_called_once_with("PATCH", "", "123456", json=patch_data)

    def test_delete_dataset(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={"id": "123456", "type": 1, "commitId": "4"},
        )
        self.gas_client.delete_dataset("test")
        open_api_do.assert_called_once_with("DELETE", "", "123456")
