#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.exception import ResourceNotExistError, ResponseError, StatusError

from .utility import get_dataset_name


class TestDataset:
    def test_create_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name)
        assert dataset_client.status.commit_id == ROOT_COMMIT_ID
        assert dataset_client.status.draft_number is None
        assert not dataset_client.status.is_draft
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    def test_create_dataset_with_region(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        regions = ("beijing", "hangzhou", "shanghai")

        for region in regions:
            dataset_name = get_dataset_name()
            gas_client.create_dataset(dataset_name, region=region)
            gas_client.get_dataset(dataset_name)

            gas_client.delete_dataset(dataset_name)

        region = "guangzhou"
        dataset_name = get_dataset_name()
        with pytest.raises(ResponseError):
            gas_client.create_dataset(dataset_name, region=region)

    def test_create_fusion_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        assert dataset_client.status.commit_id == ROOT_COMMIT_ID
        assert dataset_client.status.draft_number is None
        assert not dataset_client.status.is_draft
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name, is_fusion=True)

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
        dataset_client.create_draft("v_test")

        dataset_client_1 = gas_client.get_dataset(dataset_name)
        assert dataset_client_1.status.commit_id == ROOT_COMMIT_ID
        assert dataset_client_1.status.draft_number is None
        assert not dataset_client_1.status.is_draft
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client_1.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit("Test", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit("Test", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client = gas_client.get_dataset(dataset_name)
        assert dataset_client.status.commit_id == v2_commit_id
        assert dataset_client.status.draft_number is None
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_fusion_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit("Test", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit("Test", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client = gas_client.get_dataset(dataset_name, is_fusion=True)
        assert dataset_client.status.commit_id == v2_commit_id
        assert dataset_client.status.draft_number is None
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_rename_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test")
        dataset_client.commit("Test", tag="V1")

        new_dataset_name = f"{get_dataset_name()}new"
        gas_client.rename_dataset(name=dataset_name, new_name=new_dataset_name)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name)
        gas_client.get_dataset(new_dataset_name)

        gas_client.delete_dataset(new_dataset_name)

    def test_delete_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = get_dataset_name()
        gas_client.create_dataset(dataset_name_1)

        gas_client.delete_dataset(dataset_name_1)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name_1)

        dataset_name_2 = get_dataset_name()
        dataset_client_2 = gas_client.create_dataset(dataset_name_2)
        dataset_client_2.create_draft("v_test")
        dataset_client_2.commit("Test", tag="V1")
        gas_client.delete_dataset(dataset_name_2)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name_2)

    def test_checkout(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id
        # Neither revision nor draft number is given
        with pytest.raises(TypeError):
            dataset_client.checkout()
        # Both revision and draft number are given
        with pytest.raises(TypeError):
            dataset_client.checkout(revision=commit_1_id, draft_number=3)
        dataset_client.checkout(revision=commit_1_id)
        assert dataset_client._status.branch_name is None
        assert dataset_client._status.commit_id == commit_1_id
        # The revision does not exist.
        with pytest.raises(ResourceNotExistError):
            dataset_client.checkout(revision="123")
        assert dataset_client._status.commit_id == commit_1_id
        dataset_client.checkout(revision="V1")
        assert dataset_client._status.branch_name is None
        assert dataset_client._status.commit_id == commit_1_id
        dataset_client.checkout(revision=DEFAULT_BRANCH)
        assert dataset_client._status.branch_name == DEFAULT_BRANCH
        assert dataset_client._status.commit_id == commit_2_id

        dataset_client.create_draft("draft-3")
        # The draft does not exist.
        with pytest.raises(ResourceNotExistError):
            dataset_client.checkout(draft_number=2)
        dataset_client.checkout(draft_number=3)
        assert dataset_client._status.branch_name == DEFAULT_BRANCH
        assert dataset_client._status.draft_number == 3

        gas_client.delete_dataset(dataset_name)

    def test_notes(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(StatusError):
            dataset_client.update_notes(is_continuous=True)
        dataset_client.create_draft("draft-1")
        notes_1 = dataset_client.get_notes()
        assert notes_1.is_continuous is False

        dataset_client.update_notes(is_continuous=True)
        notes_2 = dataset_client.get_notes()
        assert notes_2.is_continuous is True

        dataset_client.update_notes(
            is_continuous=False, bin_point_cloud_fields=["X", "Y", "Z", "Intensity", "Ring"]
        )
        notes_2 = dataset_client.get_notes()
        assert notes_2.is_continuous is False
        assert notes_2.bin_point_cloud_fields == ["X", "Y", "Z", "Intensity", "Ring"]

        gas_client.delete_dataset(dataset_name)
