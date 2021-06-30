#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
import ulid

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.dataset import Data, Dataset, Frame, FusionSegment, Segment
from tensorbay.exception import FrameError, ResourceNotExistError, ResponseError
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


class TestUploadDataset:
    def test_upload_dataset_only_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
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
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        assert dataset_client.status.draft_number
        assert not dataset_client.status.commit_id

        assert dataset_client.get_notes().is_continuous is True
        assert not dataset_client.get_catalog()
        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert not segment1[0].label

        gas_client.delete_dataset(dataset_name)

    def test_upload_dataset_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
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

    def test_upload_dataset_to_given_branch(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client_1 = gas_client.create_dataset(dataset_name)
        dataset_client_1.create_draft("test")
        dataset_client_1.commit("test1")
        dataset_client_1.create_branch("dev")

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            segment.append(Data(local_path=str(local_path)))

        dataset_client_2 = gas_client.upload_dataset(dataset, branch_name="dev")
        assert dataset_client_2.status.branch_name == "dev"
        assert dataset_client_2.status.draft_number
        assert not dataset_client_2.status.commit_id

        segment1 = Segment("Segment1", client=dataset_client_2)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert not segment1[0].label

        dataset_client_2.commit("test2")
        draft_number = dataset_client_2.create_draft("test2")

        for i in range(10):
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            segment.append(Data(local_path=str(local_path)))

        dataset_client_2 = gas_client.upload_dataset(dataset, branch_name="dev")
        assert dataset_client_2.status.branch_name == "dev"
        assert dataset_client_2.status.draft_number == draft_number
        assert not dataset_client_2.status.commit_id

        with pytest.raises(ResourceNotExistError):
            gas_client.upload_dataset(dataset, branch_name="wrong")

        gas_client.delete_dataset(dataset_name)


class TestUploadSegment:
    def test_upload_segment_without_file(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("test")

        segment = Segment("segment1")

        dataset_client.upload_segment(segment)
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 0

        gas_client.delete_dataset(dataset_name)

    def test_upload_segment_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")

        segment = Segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            segment.append(data)

        dataset_client.upload_segment(segment)

        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].get_url()
        assert segment1[0].path == segment[0].target_remote_path

        gas_client.delete_dataset(dataset_name)

    def test_upload_segment_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))

        segment = Segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment.append(data)

        dataset_client.upload_segment(segment)
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].path == "hello0.txt"
        assert segment1[0].path == segment[0].target_remote_path
        assert segment1[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_upload_fusion_segment_without_file(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")

        segment = FusionSegment("segment1")

        dataset_client.upload_segment(segment)
        segment1 = FusionSegment(name="segment1", client=dataset_client)
        assert len(segment1) == 0
        assert not segment1.sensors

        gas_client.delete_dataset(dataset_name)

    def test_upload_fusion_segment_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")

        segment = FusionSegment("segment1")
        segment.sensors.add(Sensor.loads(LIDAR_DATA))

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            frame = Frame()
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            frame[LIDAR_DATA["name"]] = Data(local_path=str(local_path))
            segment.append(frame)

        dataset_client.upload_segment(segment)
        segment1 = FusionSegment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert (
            segment1[0][LIDAR_DATA["name"]].path
            == segment[0][LIDAR_DATA["name"]].target_remote_path
        )
        assert not segment1[0][LIDAR_DATA["name"]].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_upload_fusion_segment_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))

        segment = FusionSegment("segment1")
        segment.sensors.add(Sensor.loads(LIDAR_DATA))

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

        dataset_client.upload_segment(segment)
        segment1 = FusionSegment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert (
            segment1[0][LIDAR_DATA["name"]].path
            == segment[0][LIDAR_DATA["name"]].target_remote_path
        )
        assert segment1[0][LIDAR_DATA["name"]].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)


class TestUploadFrame:
    def test_upload_frame_without_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
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
        dataset_name = get_dataset_name()
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
        dataset_name = get_dataset_name()
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
        dataset_name = get_dataset_name()
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


class TestUploadData:
    def test_add_file(self, accesskey, url, tmp_path):
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

        # Add files
        for i in range(5):
            local_path = path / f"goodbye{i}.txt"
            local_path.write_text("CONTENT")
            segment_client.upload_file(local_path=str(local_path))

        data = segment_client.list_data()
        assert data[0].path == "goodbye0.txt"
        assert data[5].path == "hello0.txt"

        gas_client.delete_dataset(dataset_name)

    def test_upload_file(self, accesskey, url, tmp_path):
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

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"CONTENT"
        assert not data[0].label

        gas_client.delete_dataset(dataset_name)

    def test_upload_data_without_label(self, accesskey, url, tmp_path):
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
            segment_client.upload_data(Data(local_path=str(local_path)))

        data = segment_client.list_data()
        assert data[0].path == "hello0.txt"
        assert data[0].open().read() == b"CONTENT"
        assert not data[0].label
        # todo: match the input and output label

        gas_client.delete_dataset(dataset_name)

    def test_upload_data_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
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

    def test_upload_label_without_catalog(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
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

    def test_upload_label(self, accesskey, url, tmp_path):
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
