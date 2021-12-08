#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH, DEFAULT_IS_PUBLIC
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.exception import ResourceNotExistError, ResponseError, StatusError
from tests.utility import get_dataset_name


class TestDataset:
    def test_create_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name)
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    def test_create_public_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name, is_public=True)
        assert dataset_client.dataset_id is not None
        dataset_client_get = gas_client.get_dataset(dataset_name)
        assert dataset_client_get.is_public == True

        gas_client.delete_dataset(dataset_name)

    def test_create_fusion_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name, is_fusion=True)

        gas_client.delete_dataset(dataset_name)

    def test_create_dataset_with_alias(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        alias = f"{dataset_name}_alias"

        dataset_client = gas_client.create_dataset(dataset_name, alias=alias)
        assert dataset_client.dataset_id is not None
        dataset_client_get = gas_client.get_dataset(dataset_name)
        assert dataset_client_get.alias == alias

        gas_client.delete_dataset(dataset_name)

    def test_list_dataset_names(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)

        datasets = gas_client.list_dataset_names()
        assert dataset_name in datasets

        gas_client.delete_dataset(dataset_name)

    def test_get_new_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        dataset_client_get = gas_client.get_dataset(dataset_name)
        assert dataset_client_get.status.commit_id == ROOT_COMMIT_ID
        assert dataset_client_get.status.branch_name == DEFAULT_BRANCH
        assert dataset_client_get.dataset_id == dataset_client.dataset_id
        assert dataset_client_get.is_public == DEFAULT_IS_PUBLIC

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit("v_test_1", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit("v_test_2", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client_get = gas_client.get_dataset(dataset_name)
        assert dataset_client_get.status.commit_id == v2_commit_id
        assert dataset_client_get.status.branch_name == DEFAULT_BRANCH
        assert dataset_client_get.is_public == DEFAULT_IS_PUBLIC

        gas_client.delete_dataset(dataset_name)

    def test_get_fusion_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit("v_test_1", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit("v_test_2", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client_get = gas_client.get_dataset(dataset_name, is_fusion=True)
        assert dataset_client_get.status.commit_id == v2_commit_id
        assert dataset_client_get.status.branch_name == DEFAULT_BRANCH
        assert dataset_client_get.is_public == DEFAULT_IS_PUBLIC

        gas_client.delete_dataset(dataset_name)

    def test_update_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)

        new_dataset_alias = f"{get_dataset_name()}alias"
        gas_client.update_dataset(name=dataset_name, alias=new_dataset_alias, is_public=True)
        dataset_client_get = gas_client.get_dataset(dataset_name)
        assert dataset_client_get.alias == new_dataset_alias
        assert dataset_client_get.is_public is True
        gas_client.delete_dataset(dataset_name)

    def test_rename_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        new_dataset_name = f"{get_dataset_name()}new"
        gas_client.rename_dataset(name=dataset_name, new_name=new_dataset_name)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name)
        dataset_client_get = gas_client.get_dataset(new_dataset_name)
        assert dataset_client_get.status.commit_id == dataset_client.status.commit_id
        assert dataset_client_get.status.branch_name == dataset_client.status.branch_name
        assert dataset_client_get.dataset_id == dataset_client.dataset_id

        gas_client.delete_dataset(new_dataset_name)

    def test_delete_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = get_dataset_name()
        gas_client.create_dataset(dataset_name_1)

        # Delete new dataset
        gas_client.delete_dataset(dataset_name_1)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name_1)

        # Delete dataset including commit
        dataset_with_commit_name = get_dataset_name()
        dataset_client_2 = gas_client.create_dataset(dataset_with_commit_name)
        dataset_client_2.create_draft("v_test")
        dataset_client_2.commit("Test", tag="V1")
        gas_client.delete_dataset(dataset_with_commit_name)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_with_commit_name)

    def test_checkout(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        commit_1_tag = "V1"

        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id

        dev_branch = "dev"
        dataset_client.create_branch(dev_branch)
        dataset_client.create_draft("draft-3")
        draft_3_number = dataset_client.status.draft_number

        # Neither revision nor draft number is given
        with pytest.raises(TypeError):
            dataset_client.checkout()
        # Both revision and draft number are given
        with pytest.raises(TypeError):
            dataset_client.checkout(revision=commit_1_id, draft_number=3)

        # Checkout to a commit(branch name will be None)
        dataset_client.checkout(revision=commit_1_id)
        assert dataset_client.status.branch_name is None
        assert dataset_client.status.commit_id == commit_1_id

        # Checkout to a tag(branch name will be None)
        dataset_client.checkout(revision=commit_1_tag)
        assert dataset_client.status.branch_name is None
        assert dataset_client.status.commit_id == commit_1_id

        # Checkout to a branch: DEFAULT_BRANCH(branch name will be DEFAULT_BRANCH)
        dataset_client.checkout(revision=DEFAULT_BRANCH)
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.status.commit_id == commit_2_id

        # Checkout to anther branch
        dataset_client.checkout(revision=dev_branch)
        assert dataset_client.status.branch_name == dev_branch
        assert dataset_client.status.commit_id == commit_2_id

        # Checkout to a draft(branch name will be the relevant one)
        dataset_client.checkout(draft_number=draft_3_number)
        assert dataset_client.status.branch_name == dev_branch
        assert dataset_client.status.draft_number == draft_3_number

        # The revision does not exist.
        with pytest.raises(ResourceNotExistError):
            dataset_client.checkout(revision="123")

        # The draft does not exist.
        with pytest.raises(ResourceNotExistError):
            dataset_client.checkout(draft_number=4)

        gas_client.delete_dataset(dataset_name)

    def test_notes(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(StatusError):
            dataset_client.update_notes(is_continuous=True)
        dataset_client.create_draft("draft-1")
        origin_notes = dataset_client.get_notes()
        assert origin_notes.is_continuous is False
        assert origin_notes.bin_point_cloud_fields is None

        dataset_client.update_notes(
            is_continuous=True, bin_point_cloud_fields=["X", "Y", "Z", "Intensity", "Ring"]
        )
        modified_notes = dataset_client.get_notes()
        assert modified_notes.is_continuous is True
        assert modified_notes.bin_point_cloud_fields == ["X", "Y", "Z", "Intensity", "Ring"]

        gas_client.delete_dataset(dataset_name)
