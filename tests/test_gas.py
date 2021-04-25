#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestGAS"""

import pytest

from tensorbay.client import GAS
from tensorbay.dataset import Data, Dataset, Segment
from tensorbay.exception import ResourceNotExistError, ResponseError
from tensorbay.label import Catalog, Label

from .utility import get_random_dataset_name

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
    "BOX2D": [
        {
            "category": "01",
            "attributes": {"Vertical angle": -90, "Horizontal angle": 60, "Serie": 1, "Number": 5},
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}


class TestGAS:
    def test_create_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name)
        assert dataset_client.status.commit_id is None
        assert dataset_client.status.draft_number is None
        assert not dataset_client.status.is_draft
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    def test_create_dataset_with_region(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        regions = ("beijing", "hangzhou", "shanghai")

        for region in regions:
            dataset_name = get_random_dataset_name()
            gas_client.create_dataset(dataset_name, region=region)
            gas_client.get_dataset(dataset_name)

            gas_client.delete_dataset(dataset_name)

        region = "guangzhou"
        dataset_name = get_random_dataset_name()
        with pytest.raises(ResponseError):
            gas_client.create_dataset(dataset_name, region=region)

    def test_create_fusion_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()

        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        assert dataset_client.status.commit_id is None
        assert dataset_client.status.draft_number is None
        assert not dataset_client.status.is_draft
        assert dataset_client._name == dataset_name
        assert dataset_client.dataset_id is not None
        gas_client.get_dataset(dataset_name, is_fusion=True)

        gas_client.delete_dataset(dataset_name)

    def test_list_dataset_names(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        gas_client.create_dataset(dataset_name)

        datasets = gas_client.list_dataset_names()
        assert dataset_name in datasets
        dataset_name_1 = get_random_dataset_name()
        assert dataset_name_1 not in datasets

        gas_client.delete_dataset(dataset_name)

    def test_get_new_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test")

        dataset_client_1 = gas_client.get_dataset(dataset_name)
        assert dataset_client_1.status.commit_id is None
        assert dataset_client_1.status.draft_number is None
        assert dataset_client.status.is_draft
        assert dataset_client_1.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit(message="Test", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit(message="Test", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client = gas_client.get_dataset(dataset_name)
        assert dataset_client.status.commit_id == v2_commit_id
        assert dataset_client.status.draft_number is None
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_get_fusion_dataset_to_latest_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("v_test_1")
        dataset_client.commit(message="Test", tag="V1")
        dataset_client.create_draft("v_test_2")
        dataset_client.commit(message="Test", tag="V2")
        v2_commit_id = dataset_client.status.commit_id

        dataset_client = gas_client.get_dataset(dataset_name, is_fusion=True)
        assert dataset_client.status.commit_id == v2_commit_id
        assert dataset_client.status.draft_number is None
        assert dataset_client.name == dataset_name
        assert dataset_client.dataset_id is not None

        gas_client.delete_dataset(dataset_name)

    def test_rename_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("v_test")
        dataset_client.commit(message="Test", tag="V1")

        new_dataset_name = get_random_dataset_name()
        gas_client.rename_dataset(name=dataset_name, new_name=new_dataset_name)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name)
        gas_client.get_dataset(new_dataset_name)

        gas_client.delete_dataset(new_dataset_name)

    def test_upload_dataset_only_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        gas_client.create_dataset(dataset_name)

        dataset = Dataset(name=dataset_name)
        dataset.notes.is_continuous = True
        segment = dataset.create_segment("Segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment.append(Data(local_path=str(local_path)))

        dataset_client = gas_client.upload_dataset(dataset)
        assert dataset_client.get_notes().is_continuous == True
        assert not dataset_client.get_catalog()
        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert not segment1[0].label

        gas_client.delete_dataset(dataset_name)

    def test_upload_dataset_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        gas_client.create_dataset(dataset_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        # When uploading label, upload catalog first.
        dataset._catalog = Catalog.loads(CATALOG)

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        assert dataset_client.get_catalog()
        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert segment1[0].label

        gas_client.delete_dataset(dataset_name)

    def test_upload_dataset_to_given_draft(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client_1 = gas_client.create_dataset(dataset_name)
        draft_number = dataset_client_1.create_draft("test")

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment.append(Data(local_path=str(local_path)))

        dataset_client_2 = gas_client.upload_dataset(dataset, draft_number=draft_number)
        segment1 = Segment("Segment1", client=dataset_client_2)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert not segment1[0].label

        with pytest.raises(ResourceNotExistError):
            gas_client.upload_dataset(dataset, draft_number=draft_number + 1)

        gas_client.delete_dataset(dataset_name)

    def test_delete_dataset(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = get_random_dataset_name()
        gas_client.create_dataset(dataset_name_1)

        gas_client.delete_dataset(dataset_name_1)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name_1)

        dataset_name_2 = get_random_dataset_name()
        dataset_client_2 = gas_client.create_dataset(dataset_name_2)
        dataset_client_2.create_draft("v_test")
        dataset_client_2.commit(message="Test", tag="V1")
        gas_client.delete_dataset(dataset_name_2)
        with pytest.raises(ResourceNotExistError):
            gas_client.get_dataset(dataset_name_2)
