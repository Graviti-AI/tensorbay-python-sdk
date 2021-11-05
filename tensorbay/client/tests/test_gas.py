#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os

import pytest

from tensorbay.client import gas
from tensorbay.client.cloud_storage import CloudClient
from tensorbay.client.dataset import DatasetClient, FusionDatasetClient
from tensorbay.client.gas import DEFAULT_BRANCH, DEFAULT_IS_PUBLIC, GAS
from tensorbay.client.status import Status
from tensorbay.client.struct import ROOT_COMMIT_ID, Draft
from tensorbay.client.tests.utility import mock_response
from tensorbay.dataset import Dataset
from tensorbay.exception import DatasetTypeError, ResourceNotExistError


class TestGAS:
    gas_client = GAS("Accesskey-********************************")

    def test_generate_auth_storage_configs(self, mocker):
        params = {"name": "cloud_config", "offset": 0, "limit": 128}
        response_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                },
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert (
            list(self.gas_client._generate_auth_storage_configs("cloud_config"))
            == response_data["configs"]
        )

        open_api_do.assert_called_once_with("GET", "storage-configs", "", params=params)

    @pytest.mark.parametrize("is_fusion", [True, False])
    @pytest.mark.parametrize("is_public", [True, False])
    def test_get_dataset_with_any_type(self, mocker, is_fusion, is_public):
        response_data = {
            "name": "test",
            "type": int(is_fusion),
            "defaultBranch": DEFAULT_BRANCH,
            "commitId": "4",
            "updateTime": 1622693494,
            "owner": "",
            "id": "123456",
            "alias": "alias",
            "isPublic": is_public,
        }
        get_dataset = mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        )
        dataset_client = self.gas_client._get_dataset_with_any_type(response_data["name"])
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == response_data["name"]
        assert dataset_client._dataset_id == response_data["id"]
        assert dataset_client._status.commit_id == response_data["commitId"]
        assert dataset_client._status.branch_name == response_data["defaultBranch"]
        assert dataset_client._alias == response_data["alias"]
        assert dataset_client._is_public == response_data["isPublic"]
        get_dataset.assert_called_once_with(response_data["name"])

    def test__get_dataset(self, mocker):
        with pytest.raises(ResourceNotExistError):
            self.gas_client._get_dataset("")
        mocker.patch(
            f"{gas.__name__}.GAS._list_datasets",
            return_value={"datasets": []},
        )
        with pytest.raises(ResourceNotExistError):
            self.gas_client._get_dataset("test")

        list_dataset_data = {
            "datasets": [
                {
                    "id": "123456",
                    "name": "test",
                    "type": 0,
                    "HEAD": {"commitId": "456123"},
                    "updateTime": 1622530298,
                    "owner": "",
                    "defaultBranch": DEFAULT_BRANCH,
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }

        get_dataset_data = {
            "name": "test",
            "type": 0,
            "defaultBranch": DEFAULT_BRANCH,
            "commitId": "4",
            "updateTime": 1622693494,
            "owner": "",
            "id": "123456",
            "isPublic": DEFAULT_IS_PUBLIC,
        }
        mocker.patch(
            f"{gas.__name__}.GAS._list_datasets",
            return_value=list_dataset_data,
        )
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=get_dataset_data),
        )
        assert self.gas_client._get_dataset(get_dataset_data["name"]) == get_dataset_data
        open_api_do.assert_called_once_with("GET", "", list_dataset_data["datasets"][0]["id"])

    def test__list_datasets(self, mocker):
        params = {
            "name": "test",
            "offset": 0,
            "limit": 128,
        }
        response_data = {
            "datasets": [
                {
                    "id": "123456",
                    "name": "test",
                    "type": 0,
                    "defaultBranch": DEFAULT_BRANCH,
                    "updateTime": 1622530298,
                    "owner": "",
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert self.gas_client._list_datasets(params["name"]) == response_data
        open_api_do.assert_called_once_with("GET", "", params=params)

    def test_get_user(self, mocker):
        response_data = {
            "nickname": "user_name",
            "email": "user_email",
            "mobile": "11111111111",
            "description": "",
            "team": {"name": "TensorbaySDKTest", "email": None, "description": ""},
        }
        dump_data = {
            "nickname": "user_name",
            "email": "user_email",
            "mobile": "11111111111",
            "team": {
                "name": "TensorbaySDKTest",
            },
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert self.gas_client.get_user().dumps() == dump_data
        open_api_do.assert_called_once_with("GET", "users")

    def test_get_auth_storage_config(self, mocker):
        with pytest.raises(TypeError):
            self.gas_client.get_auth_storage_config("")

        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data={"configs": [], "totalCount": 0}),
        )
        with pytest.raises(ResourceNotExistError):
            self.gas_client.get_auth_storage_config("cloud_config")

        response_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                },
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert (
            self.gas_client.get_auth_storage_config(response_data["configs"][0]["name"])
            == response_data["configs"][0]
        )

    def test_list_auth_storage_configs(self, mocker):
        response_data = {
            "configs": [
                {
                    "name": "cloud_config",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                },
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        configs = self.gas_client.list_auth_storage_configs()

        assert list(configs) == response_data["configs"]

    def test_delete_storage_config(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        self.gas_client.delete_storage_config("test-config")
        open_api_do.assert_called_once_with("DELETE", "storage-configs/test-config")

    def test_create_oss_storage_config(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        self.gas_client.create_oss_storage_config(
            "oss_config",
            "tests",
            endpoint="oss-cn-qingdao.aliyuncs.com",
            accesskey_id="accesskeyId",
            accesskey_secret="accesskeySecret",
            bucket_name="bucketName",
        )
        post_data = {
            "name": "oss_config",
            "filePath": "tests",
            "endpoint": "oss-cn-qingdao.aliyuncs.com",
            "accesskeyId": "accesskeyId",
            "accesskeySecret": "accesskeySecret",
            "bucketName": "bucketName",
        }
        open_api_do("POST", "storage-configs/oss", json=post_data)

    def test_create_s3_storage_config(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        self.gas_client.create_s3_storage_config(
            "s3_config",
            "tests",
            endpoint="s3.cn-northwest-1.amazonaws.com",
            accesskey_id="accesskeyId",
            accesskey_secret="accesskeySecret",
            bucket_name="bucketName",
        )
        post_data = {
            "name": "s3_config",
            "filePath": "tests",
            "endpoint": "s3.cn-northwest-1.amazonaws.com",
            "accesskeyId": "accesskeyId",
            "accesskeySecret": "accesskeySecret",
            "bucketName": "bucketName",
        }
        open_api_do("POST", "storage-configs/s3", json=post_data)

    def test_create_azure_storage_config(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        self.gas_client.create_azure_storage_config(
            "azure_config",
            "tests",
            account_type="China",
            account_name="accountName",
            account_key="accountKey",
            container_name="containerName",
        )
        post_data = {
            "name": "s3_config",
            "filePath": "tests",
            "accesskeyId": "accountName",
            "accesskeySecret": "accountKey",
            "containerName": "containerName",
            "accountType": "China",
        }
        open_api_do("POST", "storage-configs/azure", json=post_data)

    def test_create_local_storage_config(self, mocker):
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        self.gas_client.create_local_storage_config(
            "local_config",
            "tests",
            "http://192.168.0.1:9000",
        )
        post_data = {
            "name": "local_config",
            "filePath": "tests",
            "endpoint": "http://192.168.0.1:9000",
        }
        open_api_do("POST", "storage-configs/local", json=post_data)

    def test_get_cloud_client(self, mocker):
        config_name = "cloud_train"
        response_data = {
            "configs": [
                {
                    "name": "cloud_train",
                    "type": "azure",
                    "accountName": "tensorbay",
                    "containerName": "tensorbay",
                },
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        cloud_client = self.gas_client.get_cloud_client(config_name)
        cloud_client_1 = CloudClient(config_name, self.gas_client._client)
        assert cloud_client._name == cloud_client_1._name
        assert cloud_client._client == cloud_client_1._client

    @pytest.mark.parametrize("is_fusion", [True, False])
    @pytest.mark.parametrize("is_public", [True, False])
    def test_create_dataset(self, mocker, is_fusion, is_public):
        params = {
            "name": "test",
            "type": int(is_fusion),
            "configName": "config",
            "alias": "alias",
            "isPublic": is_public,
        }
        response_data = {"id": "12345"}
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        dataset_client = self.gas_client.create_dataset(
            "test", is_fusion, config_name="config", alias="alias", is_public=is_public
        )
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == params["name"]
        assert dataset_client._dataset_id == response_data["id"]
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.status.commit_id == ROOT_COMMIT_ID
        assert dataset_client._alias == params["alias"]
        assert dataset_client._is_public == is_public
        open_api_do.assert_called_once_with("POST", "", json=params)

    @pytest.mark.parametrize("is_fusion", [True, False])
    @pytest.mark.parametrize("is_public", [True, False])
    def test_get_dataset(self, mocker, is_fusion, is_public):
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value={
                "id": "123456",
                "type": 1,
                "commitId": "4",
                "defaultBranch": DEFAULT_BRANCH,
                "alias": "alias",
                "isPublic": is_public,
            },
        )
        with pytest.raises(DatasetTypeError):
            self.gas_client.get_dataset("test")

        response_data = {
            "id": "123456",
            "type": int(is_fusion),
            "commitId": "4",
            "defaultBranch": DEFAULT_BRANCH,
            "alias": "alias",
            "isPublic": is_public,
        }
        dataset_name = "test"
        get_dataset = mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        )
        dataset_client = self.gas_client.get_dataset(dataset_name, is_fusion)
        dataset_type = FusionDatasetClient if is_fusion else DatasetClient
        assert isinstance(dataset_client, dataset_type)
        assert dataset_client._name == dataset_name
        assert dataset_client._dataset_id == response_data["id"]
        assert dataset_client._status.commit_id == response_data["commitId"]
        assert dataset_client._status.branch_name == response_data["defaultBranch"]
        assert dataset_client._alias == response_data["alias"]
        assert dataset_client._is_public == response_data["isPublic"]
        get_dataset.assert_called_once_with(dataset_name)

    def test_list_dataset_names(self, mocker):
        params = {
            "offset": 0,
            "limit": 128,
        }
        response_data = {
            "datasets": [
                {
                    "id": "123456",
                    "name": "test",
                    "type": 0,
                    "defaultBranch": DEFAULT_BRANCH,
                    "updateTime": 1622530298,
                    "owner": "",
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )

        datasets = self.gas_client.list_dataset_names()
        assert list(datasets) == [data["name"] for data in response_data["datasets"]]
        open_api_do.assert_called_once_with("GET", "", params=params)

    def test_update_dataset(self, mocker):
        response_data = {
            "id": "123456",
            "type": 1,
            "commitId": "4",
            "defaultBranch": DEFAULT_BRANCH,
        }
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        )
        patch_data = {"alias": "new_alias", "isPublic": True}
        self.gas_client.update_dataset("test", alias="new_alias", is_public=True)
        open_api_do.assert_called_once_with("PATCH", "", response_data["id"], json=patch_data)

    def test_rename_dataset(self, mocker):
        response_data = {
            "id": "123456",
            "type": 1,
            "commitId": "4",
            "defaultBranch": DEFAULT_BRANCH,
        }
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        )
        patch_data = {"name": "new_test"}
        self.gas_client.rename_dataset("test", new_name="new_test")
        open_api_do.assert_called_once_with("PATCH", "", response_data["id"], json=patch_data)

    def test_upload_dataset(self, mocker):
        dataset = Dataset("test")
        dataset.load_catalog(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "opendataset",
                "HeadPoseImage",
                "catalog.json",
            )
        )
        for i in range(5):
            dataset.create_segment(str(i))

        # upload the dataset in main branch containing no draft
        get_dataset = mocker.patch(
            f"{gas.__name__}.GAS.get_dataset",
            return_value=DatasetClient(
                "test",
                "12345",
                self.gas_client,
                status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
                alias="",
                is_public=DEFAULT_IS_PUBLIC,
            ),
        )
        checkout = mocker.patch(f"{gas.__name__}.DatasetClient.checkout")
        list_drafts = mocker.patch(f"{gas.__name__}.DatasetClient.list_drafts", return_value=[])
        create_draft = mocker.patch(f"{gas.__name__}.DatasetClient.create_draft")
        upload_catalog = mocker.patch(f"{gas.__name__}.DatasetClient.upload_catalog")
        update_notes = mocker.patch(f"{gas.__name__}.DatasetClient.update_notes")
        _upload_segment = mocker.patch(f"{gas.__name__}.DatasetClient._upload_segment")

        self.gas_client.upload_dataset(dataset)
        assert not checkout.called
        get_dataset.assert_called_once_with(dataset.name, False)
        list_drafts.assert_called_once_with(branch_name=DEFAULT_BRANCH)
        create_draft.assert_called_once_with(
            'Draft autogenerated by "GAS.upload_dataset"', branch_name=DEFAULT_BRANCH
        )
        upload_catalog.assert_called_once_with(dataset.catalog)
        update_notes.assert_called_once_with(**dataset.notes)
        assert _upload_segment.call_count == 5

        # upload the dataset in main branch containing a draft
        list_drafts = mocker.patch(
            f"{gas.__name__}.DatasetClient.list_drafts",
            return_value=[Draft(1, "title", DEFAULT_BRANCH, "OPEN")],
        )
        checkout = mocker.patch(f"{gas.__name__}.DatasetClient.checkout")
        self.gas_client.upload_dataset(dataset)
        list_drafts.assert_called_once_with(branch_name=DEFAULT_BRANCH)
        checkout.assert_called_once_with(draft_number=1)

        # upload the dataset in dev branch containing no draft
        list_drafts = mocker.patch(
            f"{gas.__name__}.DatasetClient.list_drafts",
            return_value=[],
        )
        checkout = mocker.patch(f"{gas.__name__}.DatasetClient.checkout")
        create_draft = mocker.patch(f"{gas.__name__}.DatasetClient.create_draft")
        self.gas_client.upload_dataset(dataset, branch_name="dev")
        assert not checkout.called
        list_drafts.assert_called_once_with(branch_name="dev")
        create_draft.assert_called_once_with(
            'Draft autogenerated by "GAS.upload_dataset"', branch_name="dev"
        )

        # upload the dataset in dev branch containing a draft
        list_drafts = mocker.patch(
            f"{gas.__name__}.DatasetClient.list_drafts",
            return_value=[Draft(1, "title", "dev", "OPEN")],
        )
        checkout = mocker.patch(f"{gas.__name__}.DatasetClient.checkout")
        self.gas_client.upload_dataset(dataset, branch_name="dev")
        list_drafts.assert_called_once_with(branch_name="dev")
        checkout.assert_called_once_with(draft_number=1)

    def test_delete_dataset(self, mocker):
        response_data = {"id": "123456", "type": 1, "commitId": "4"}
        open_api_do = mocker.patch(f"{gas.__name__}.Client.open_api_do")
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        )
        self.gas_client.delete_dataset("test")
        open_api_do.assert_called_once_with("DELETE", "", response_data["id"])
