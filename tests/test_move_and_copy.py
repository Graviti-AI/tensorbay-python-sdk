#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.dataset import Data, Dataset, Frame, FusionDataset, FusionSegment, Segment
from tensorbay.exception import InvalidParamsError, ResponseSystemError
from tensorbay.label import Catalog, Label
from tensorbay.sensor import Sensor

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

LIDAR_DATA = {
    "name": "Lidar1",
    "type": "LIDAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}

WRONG_LABEL = {
    "BOX2D": [
        {
            "category": "01",
            "attributes": {"Vertical angle": -75, "Horizontal angle": 60, "Serie": 1, "Number": 5},
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}


class TestMove:
    def test_move_segment(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)
        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
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
        segment_client = dataset_client.move_segment("Segment1", "Segment2")
        assert segment_client.name == "Segment2"

        with pytest.raises(InvalidParamsError):
            dataset_client.move_segment("Segment1", "Segment3", strategy="push")

        segment2 = Segment("Segment2", client=dataset_client)
        assert segment2[0].path == "hello0.txt"
        assert segment2[0].path == segment[0].target_remote_path
        assert segment2[0].label

        gas_client.delete_dataset(dataset_name)

    def test_move_fusion_segment(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset = FusionDataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        segment.sensors.add(Sensor.loads(LIDAR_DATA))
        dataset._catalog = Catalog.loads(CATALOG)
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            frame = Frame()
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            frame[LIDAR_DATA["name"]] = data
            segment.append(frame)

        dataset_client = gas_client.upload_dataset(dataset)
        segment_client = dataset_client.move_segment("Segment1", "Segment2")
        assert segment_client.name == "Segment2"

        with pytest.raises(InvalidParamsError):
            dataset_client.move_segment("Segment1", "Segment3", strategy="push")

        segment2 = FusionSegment("Segment2", client=dataset_client)
        assert segment2[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert (
            segment2[0][LIDAR_DATA["name"]].path
            == segment[0][LIDAR_DATA["name"]].target_remote_path
        )
        assert segment2[0][LIDAR_DATA["name"]].label

        gas_client.delete_dataset(dataset_name)

    def test_move_segment_abort(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)
        dataset = Dataset(name=dataset_name)
        segment1 = dataset.create_segment("Segment1")
        dataset._catalog = Catalog.loads(CATALOG)
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment1.append(data)

        segment2 = dataset.create_segment("Segment2")
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment2.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        with pytest.raises(ResponseSystemError):
            dataset_client.move_segment("Segment1", "Segment2")

        gas_client.delete_dataset(dataset_name)
