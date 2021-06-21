#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
import pytest

from tensorbay import GAS
from tensorbay.dataset import Data
from tensorbay.label import Catalog, Label

from .utility import get_dataset_name

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
NEW_LABEL = {
    "BOX2D": [
        {
            "category": "01",
            "attributes": {"Vertical angle": -60, "Horizontal angle": 60, "Serie": 1, "Number": 5},
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}


class TestData:
    def test_delete_data(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment_client.upload_data(data)

        with pytest.raises(NotImplementedError):
            segment_client.delete_data("hello0.txt")
        data_paths = segment_client.list_data_paths()
        # assert "hello0.txt" not in data_paths

        with pytest.raises(NotImplementedError):
            segment_client.delete_data(segment_client.list_data_paths())
        data = segment_client.list_data()
        # assert len(data) == 0

        gas_client.delete_dataset(dataset_name)

    def test_list_file_order(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        # Upload files in reverse order
        for i in reversed(range(5)):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        # Add files in reverse order
        for i in reversed(range(5)):
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data = segment_client.list_data()
        assert data[0].path == "goodbye0.txt"
        assert data[5].path == "hello0.txt"

        gas_client.delete_dataset(dataset_name)

    def test_list_data_paths(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        # Add other files in reverse order
        for i in reversed(range(5)):
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data_paths = segment_client.list_data_paths()
        assert data_paths[0] == "goodbye0.txt"
        assert data_paths[5] == "hello0.txt"

        gas_client.delete_dataset(dataset_name)

    def test_overwrite_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        # Replace files
        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("ADD CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"ADD CONTENT"
        assert not data[0].label

        gas_client.delete_dataset(dataset_name)

    def test_overwrite_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()
        local_path = path / "hello0.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        segment_client.upload_file(data.path, data.target_remote_path)

        data.label = Label.loads(LABEL)
        segment_client.upload_label(data)

        # Replace labels
        data.label = Label.loads(NEW_LABEL)
        segment_client.upload_label(data)

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)
