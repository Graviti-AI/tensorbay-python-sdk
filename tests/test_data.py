#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
import os

import numpy as np
import pytest

from tensorbay import GAS
from tensorbay.dataset import Data, Frame
from tensorbay.label import Catalog, InstanceMask, Label, PanopticMask, SemanticMask
from tensorbay.label.label_mask import RemoteInstanceMask, RemotePanopticMask, RemoteSemanticMask
from tensorbay.sensor import Sensor
from tests.utility import get_dataset_name

CATALOG_ATTRBUTES = [
    {"name": "gender", "enum": ["male", "female"]},
    {"name": "occluded", "type": "integer", "minimum": 1, "maximum": 5},
]
MASK_CATALOG_CONTENTS = {
    "categories": [
        {"name": "cat", "description": "This is an exmaple of test", "categoryId": 0},
        {"name": "dog", "description": "This is an exmaple of test", "categoryId": 1},
    ],
    "attributes": CATALOG_ATTRBUTES,
}
BOX2D_CATALOG_CONTENTS = {
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
BOX2D_CATALOG = {"BOX2D": BOX2D_CATALOG_CONTENTS}
CATALOG = {
    "BOX2D": BOX2D_CATALOG_CONTENTS,
    "SEMANTIC_MASK": MASK_CATALOG_CONTENTS,
    "INSTANCE_MASK": MASK_CATALOG_CONTENTS,
    "PANOPTIC_MASK": MASK_CATALOG_CONTENTS,
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
LIDAR_DATA = {
    "name": "Lidar1",
    "type": "LIDAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}
SEMANTIC_MASK_LABEL = {
    "remotePath": "hello.png",
    "info": [
        {"categoryId": 0, "attributes": {"occluded": True}},
        {"categoryId": 1, "attributes": {"occluded": False}},
    ],
}
INSTANCE_MASK_LABEL = {
    "remotePath": "hello.png",
    "info": [
        {"instanceId": 0, "attributes": {"occluded": True}},
        {"instanceId": 1, "attributes": {"occluded": False}},
    ],
}
PANOPTIC_MASK_LABEL = {
    "remotePath": "hello.png",
    "info": [
        {"instanceId": 100, "categoryId": 0, "attributes": {"occluded": True}},
        {"instanceId": 101, "categoryId": 1, "attributes": {"occluded": False}},
    ],
}


@pytest.fixture
def mask_file(tmp_path):
    local_path = tmp_path / "hello.png"
    mask = np.random.randint(0, 1, 48).reshape(8, 6)
    mask.dump(local_path)
    return local_path


class TestData:
    def test_get_data(self, accesskey, url, tmp_path, mask_file):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        # Upload data with label
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text(f"CONTENT{i}")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)

            semantic_mask = SemanticMask(str(mask_file))
            semantic_mask.all_attributes = {0: {"occluded": True}, 1: {"occluded": False}}
            data.label.semantic_mask = semantic_mask

            instance_mask = InstanceMask(str(mask_file))
            instance_mask.all_attributes = {0: {"occluded": True}, 1: {"occluded": False}}
            data.label.instance_mask = instance_mask

            panoptic_mask = PanopticMask(str(mask_file))
            panoptic_mask.all_category_ids = {100: 0, 101: 1}
            data.label.panoptic_mask = panoptic_mask
            segment_client.upload_data(data)

        for i in range(10):
            data = segment_client.get_data(f"hello{i}.txt")
            assert data.path == f"hello{i}.txt"
            assert data.label.box2d == Label.loads(LABEL).box2d

            stem = os.path.splitext(data.path)[0]
            remote_semantic_mask = data.label.semantic_mask
            semantic_mask = RemoteSemanticMask.from_response_body(SEMANTIC_MASK_LABEL)
            assert remote_semantic_mask.path == f"{stem}.png"
            assert remote_semantic_mask.all_attributes == semantic_mask.all_attributes

            remote_instance_mask = data.label.instance_mask
            instance_mask = RemoteInstanceMask.from_response_body(INSTANCE_MASK_LABEL)
            assert remote_instance_mask.path == f"{stem}.png"
            assert remote_instance_mask.all_attributes == instance_mask.all_attributes

            remote_panoptic_mask = data.label.panoptic_mask
            panoptic_mask = RemotePanopticMask.from_response_body(PANOPTIC_MASK_LABEL)
            assert remote_panoptic_mask.path == f"{stem}.png"
            assert remote_panoptic_mask.all_category_ids == panoptic_mask.all_category_ids

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
        dataset_client.upload_catalog(Catalog.loads(BOX2D_CATALOG))
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

    def test_delete_data(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(BOX2D_CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text(f"CONTENT{i}")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment_client.upload_data(data)

        segment_client.delete_data("hello0.txt")
        data_paths = segment_client.list_data_paths()
        assert "hello0.txt" not in data_paths

        gas_client.delete_dataset(dataset_name)

    def test_delete_frame(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(BOX2D_CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")
        segment_client.upload_sensor(Sensor.loads(LIDAR_DATA))

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(5):
            frame = Frame()
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            frame[LIDAR_DATA["name"]] = data
            segment_client.upload_frame(frame, timestamp=i)

        frame_1_id = segment_client.list_frames()[0].frame_id
        segment_client.delete_frame(frame_1_id)
        frame_ids = [frame.frame_id for frame in segment_client.list_frames()]
        assert frame_1_id not in frame_ids

        gas_client.delete_dataset(dataset_name)
