#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestSegmentClient"""

import pytest
import ulid

from tensorbay import __version__
from tensorbay.client.gas import GAS
from tensorbay.dataset.data import Data, Label
from tensorbay.dataset.frame import Frame
from tensorbay.exception import FrameError, ResponseError
from tensorbay.label.catalog import Catalog
from tensorbay.sensor.sensor import Sensor, Sensors

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

NEW_LABEL = {
    "BOX2D": [
        {
            "category": "01",
            "attributes": {"Vertical angle": -60, "Horizontal angle": 60, "Serie": 1, "Number": 5},
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
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

LIDAR_DATA = {
    "name": "Lidar1",
    "type": "LIDAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}

RADAR_DATA = {
    "name": "Radar1",
    "type": "RADAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}


class TestSegmentClient:
    """Test SegmentClient class."""

    def test_upload_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"CONTENT"
        assert not data[0].label

        gas_client.delete_dataset(dataset_name)

    def test_replace_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_add_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        # Add files
        for i in range(5):
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data = segment_client.list_data()
        assert data[0].path == "goodbye0.txt"
        assert data[5].path == "hello0.txt"

        gas_client.delete_dataset(dataset_name)

    def test_list_file_order(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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
        dataset_name = get_random_dataset_name()
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

    @pytest.mark.xfail(__version__ < "1.5.0", reason="not supported at least until v1.5.0")
    def test_upload_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        local_path = path / "hello0.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        data.label = Label.loads(LABEL)
        # If not uploading file, uploading label is not allowed
        with pytest.raises(ResponseError):
            segment_client.upload_label(data)

        # Uploading files
        segment_client.upload_file(data.path, data.target_remote_path)

        data.label = Label.loads(WRONG_LABEL)
        # Uploading wrong label is not allowed
        with pytest.raises(ResponseError):
            segment_client.upload_label(data)
        data.label = Label.loads(LABEL)
        segment_client.upload_label(data)

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_replace_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_upload_label_without_catalog(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()
        local_path = path / "hello0.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        segment_client.upload_file(data.path, data.target_remote_path)

        # If not uploading catalog, uploading label is not allowed
        data.label = Label.loads(LABEL)
        with pytest.raises(ResponseError):
            segment_client.upload_label(data)

        gas_client.delete_dataset(dataset_name)

    def test_upload_data_without_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()

        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_data(Data(local_path=str(local_path)))

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"CONTENT"
        assert not data[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_upload_data_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        segment_client = dataset_client.get_or_create_segment("segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment_client.upload_data(data)

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"CONTENT"
        assert data[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_delete_data(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

        segment_client.delete_data("hello0.txt")
        data_paths = segment_client.list_data_paths()
        assert "hello0.txt" not in data_paths

        segment_client.delete_data(segment_client.list_data_paths())
        data = segment_client.list_data()
        assert len(data) == 0

        gas_client.delete_dataset(dataset_name)

    def test_sensor(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")

        segment_client.upload_sensor(Sensor.loads(LIDAR_DATA))

        sensors = segment_client.get_sensors()
        assert sensors == Sensors.loads([LIDAR_DATA])

        segment_client.delete_sensor(LIDAR_DATA["name"])
        sensors = segment_client.get_sensors()
        assert len(sensors) == 0

        gas_client.delete_dataset(dataset_name)

    def test_upload_frame_without_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")

        segment_client.upload_sensor(Sensor.loads(LIDAR_DATA))

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(5):
            frame = Frame()
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            frame[LIDAR_DATA["name"]] = data
            segment_client.upload_frame(frame, timestamp=i)

        frames = segment_client.list_frames()
        assert len(frames) == 5
        assert frames[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert not frames[0][LIDAR_DATA["name"]].label

        gas_client.delete_dataset(dataset_name)

    def test_upload_frame_without_sensor(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")

        path = tmp_path / "sub"
        path.mkdir()

        frame = Frame()
        local_path = path / "hello0.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        frame[LIDAR_DATA["name"]] = data

        # If not uploading sensor, uploading frame is not allowed
        with pytest.raises(ResponseError):
            segment_client.upload_frame(frame, timestamp=0)

        gas_client.delete_dataset(dataset_name)

    def test_upload_frame_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
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

        frames = segment_client.list_frames()
        assert len(frames) == 5
        assert frames[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert frames[0][LIDAR_DATA["name"]].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_upload_frame_with_order(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment1")

        segment_client.upload_sensor(Sensor.loads(LIDAR_DATA))

        path = tmp_path / "sub"
        path.mkdir()
        # If noe setting frame id in frame, set timestamp(order) when uploading
        for i in reversed(range(5)):
            frame = Frame()
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            frame[LIDAR_DATA["name"]] = data
            segment_client.upload_frame(frame, timestamp=i)

        # Set frame id in frame
        for i in range(5, 10):
            frame = Frame(frame_id=ulid.from_timestamp(i))
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            frame[LIDAR_DATA["name"]] = data
            segment_client.upload_frame(frame)

        # Both setting frame id in frame and set timestamp(order) when uploading are not allowed
        i = 10
        frame = Frame(frame_id=ulid.from_timestamp(i))
        local_path = path / f"goodbye{i}.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        frame[LIDAR_DATA["name"]] = data
        with pytest.raises(FrameError):
            segment_client.upload_frame(frame, timestamp=i)

        # Neither setting frame id in frame nor set timestamp(order) when uploading is not allowed
        frame = Frame()
        local_path = path / f"goodbye{i}.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        frame[LIDAR_DATA["name"]] = data
        with pytest.raises(FrameError):
            segment_client.upload_frame(frame)

        frames = segment_client.list_frames()
        assert len(frames) == 10
        assert frames[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert frames[5][LIDAR_DATA["name"]].path == "goodbye5.txt"
        assert not frames[0][LIDAR_DATA["name"]].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)
