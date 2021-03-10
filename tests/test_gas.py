#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestGAS"""

import uuid

import pytest

from tensorbay.client import GAS, GASDatasetError, GASResponseError
from tensorbay.dataset import Data, Dataset, Segment

CATALOG = {
    "BOX2D": {
        "categories": [
            {"name": "01"},
            {"name": "02"},
            {"name": "03"},
            {"name": "04"},
            {"name": "05"},
            {"name": "06"},
            {"name": "07"},
            {"name": "08"},
            {"name": "09"},
            {"name": "10"},
            {"name": "11"},
            {"name": "12"},
            {"name": "13"},
            {"name": "14"},
            {"name": "15"},
        ],
        "attributes": [
            {"name": "Vertical angle", "enum": [-90, -60, -30, -15, 0, 15, 30, 60, 90]},
            {
                "name": "Horizontal angle",
                "enum": [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90],
            },
            {"name": "Serie", "enum": [1, 2]},
            {"name": "Number", "type": "integer", "minimum": 0, "maximum": 92},
        ],
    }
}

LABEL = {
    "BOX2D": {
        "category": "01",
        "attributes": {"Vertical angle": -90, "Horizontal angle": 60, "Serie": 1, "Number": 5},
        "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
    }
}


class TestGAS:
    def test_create_dataset(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")

        dataset_client = gas_client.create_dataset(dataset_name)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    def test_create_dataset_with_region(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        if "dev" in url:
            regions = ["beijing", "hangzhou", "qingdao"]
        elif "fat" in url:
            regions = ["beijing", "hangzhou", "qingdao"]
        elif "uat" in url:
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

    def test_create_fusion_dataset(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")

        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name, is_fusion=True)

        gas_client.delete_dataset(dataset_name)

    def test_list_dataset_names(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name)

        datasets = list(gas_client.list_dataset_names())
        assert dataset_name in datasets

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_draft(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name)

        dataset_client = gas_client.get_dataset(dataset_name)
        assert dataset_client.commit_id is None
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_commit_dataset(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
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

    def test_get_dataset_with_commit_id(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = "test" + str(uuid.uuid4()).replace("-", "")
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.commit(message="Test", tag="V1")
        v1_commit_id = dataset_client.commit_id

        dataset_client = gas_client.get_dataset(dataset_name, commit_id=v1_commit_id)
        assert dataset_client.commit_id == v1_commit_id
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_fusion_dataset_with_commit_id(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
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

    def test_rename_dataset(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
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

    def test_upload_dataset_with_data(self, accesskey, url, tmp_path) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = "test" + str(uuid.uuid4()).replace("-", "")
        gas_client.create_dataset(dataset_name_1)

        dataset = Dataset(name=dataset_name_1)
        segment = dataset.create_segment("Segment1")
        dataset.catalog.loads(CATALOG)

        d = tmp_path / "sub"
        d.mkdir()
        for i in range(100):
            p = d / "hello{}.txt".format(i)
            p.write_text("CONTENT")
            segment.append(Data(local_path=str(p)))

        dataset_client = gas_client.upload_dataset(dataset)
        assert dataset_client.get_catalog()
        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) > 0
        assert segment1[0].path != "hello0.txt"
        assert not segment1[0].label

        gas_client.upload_dataset(dataset)

    def test_delete_dataset(self, accesskey, url) -> None:
        gas_client = GAS(access_key=accesskey, url=url)
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
