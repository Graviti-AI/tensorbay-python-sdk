#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestGAS"""

import uuid

import pytest

from ..client import *
from ..dataset import *
from .common import *


class TestGAS:
    """Integration Test for GAS class."""

    def test_create_dataset(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")

        dataset_client = gas_client.create_dataset(dataset_name)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    def test_create_dataset_with_region(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        if "dev" in BASE_URL:
            regions = ["beijing", "hangzhou", "qingdao"]
        elif "fat" in BASE_URL:
            regions = ["beijing", "hangzhou", "qingdao"]
        elif "uat" in BASE_URL:
            regions = ["beijing", "hangzhou", "qingdao"]
        else:
            regions = ["beijing", "hangzhou", "shanghai"]

        for region in regions:
            dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
            gas_client.create_dataset(dataset_name, region=region)
            gas_client.get_dataset(dataset_name)

            gas_client.delete_dataset(dataset_name)

        region = "guangzhou"
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        with pytest.raises(GASResponseError):
            gas_client.create_dataset(dataset_name, region=region)

    def test_create_fusion_dataset(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")

        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name, is_fusion=True)

        gas_client.delete_dataset(dataset_name)

    def test_list_dataset_names(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name)

        datasets = list(gas_client.list_dataset_names())
        assert dataset_name in datasets

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_draft(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name)

        dataset_client = gas_client.get_dataset(dataset_name)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_commit_dataset(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client = gas_client.create_dataset(dataset_name)

        dataset_client.commit(message="Test", tag="V1")
        v1_commit_id = dataset_client.commit_id
        assert v1_commit_id is not None

        dataset_client.commit(message="Test", tag="V2")
        v2_commit_id = dataset_client.commit_id
        assert v2_commit_id is not None
        assert v2_commit_id != v1_commit_id
        gas_client.get_dataset(dataset_name, commit_id=dataset_client.commit_id)

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_with_commit_id(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.commit(message="Test", tag="V1")
        v1_commit_id = dataset_client.commit_id

        dataset_client = gas_client.get_dataset(dataset_name, commit_id=v1_commit_id)
        assert dataset_client.commit_id == v1_commit_id
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_fusion_dataset_with_commit_id(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.commit(message="Test", tag="V1")
        v1_commit_id = dataset_client.commit_id

        dataset_client = gas_client.get_dataset(
            dataset_name, is_fusion=True, commit_id=v1_commit_id
        )
        assert dataset_client.commit_id == v1_commit_id
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_rename_dataset(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.commit(message="Test", tag="V1")

        new_dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.rename_dataset(name=dataset_name, new_name=new_dataset_name)
        with pytest.raises(GASDatasetError):
            gas_client.get_dataset(dataset_name, commit_id=dataset_client.commit_id)
        with pytest.raises(GASDatasetError):
            gas_client.get_dataset(dataset_name)
        gas_client.get_dataset(new_dataset_name)

        gas_client.delete_dataset(new_dataset_name)

    def test_upload_dataset_without_data(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name_1 = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name_1)

        dataset = Dataset(name=dataset_name_1)
        segment = dataset.create_segment("Segment1")
        gas_client.upload_dataset_object(dataset)

    def test_delete_dataset(self) -> None:
        gas_client = GAS(access_key=ACCESS_KEY, url=BASE_URL)
        dataset_name_1 = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name_1)

        gas_client.delete_dataset(dataset_name_1)
        with pytest.raises(GASDatasetError):
            gas_client.get_dataset(dataset_name_1)

        dataset_name_2 = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client_2 = gas_client.create_dataset(dataset_name_2)
        dataset_client_2.commit(message="Test", tag="V1")
        with pytest.raises(GASDatasetError):
            gas_client.get_dataset(dataset_name_1, commit_id=dataset_client_2.commit_id)
