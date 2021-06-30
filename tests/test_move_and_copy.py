#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.dataset import Data, Dataset, Frame, FusionDataset, FusionSegment, Segment
from tensorbay.exception import InvalidParamsError, ResourceNotExistError, ResponseSystemError
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

    def test_move_segment_override(self, accesskey, url, tmp_path):
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
            local_path.write_text("CONTENT_1")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment1.append(data)

        segment2 = dataset.create_segment("Segment2")
        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT_2")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment2.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.move_segment("Segment1", "Segment2", strategy="override")

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_segment("Segment1")

        segment_moved = Segment("Segment2", client=dataset_client)
        assert segment_moved[0].path == "hello0.txt"
        assert segment_moved[0].path == segment1[0].target_remote_path
        assert segment_moved[0].open().read() == b"CONTENT_1"
        assert segment_moved[0].label

        gas_client.delete_dataset(dataset_name)

    def test_move_segment_skip(self, accesskey, url, tmp_path):
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
            local_path.write_text("CONTENT_1")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment1.append(data)

        segment2 = dataset.create_segment("Segment2")
        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT_2")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment2.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.move_segment("Segment1", "Segment2", strategy="skip")

        segment_moved = Segment("Segment2", client=dataset_client)
        assert segment_moved[0].path == "hello10.txt"
        assert segment_moved[0].path == segment2[0].target_remote_path
        assert segment_moved[0].open().read() == b"CONTENT_2"
        assert segment_moved[0].label

        gas_client.delete_dataset(dataset_name)

    def test_move_data(self, accesskey, url, tmp_path):
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
        segment_client = dataset_client.get_segment("Segment1")

        segment_client.move_data("hello0.txt", "goodbye0.txt")
        segment_client.move_data("hello9.txt", "goodbye1.txt")

        # with pytest.raises(InvalidParamsError):
        #     segment_client.move_data("hello1.txt", "goodbye2.txt", strategy="push")
        segment2 = Segment("Segment1", client=dataset_client)
        assert segment2[0].path == "goodbye0.txt"
        assert segment2[1].path == "goodbye1.txt"
        assert segment2[9].path == "hello8.txt"
        assert segment2[0].label

        gas_client.delete_dataset(dataset_name)

    # @pytest.mark.xfail(__version__ < "1.9.0", reason="not supported until 1.9.0")
    # def test_move_data_override(self, accesskey, url, tmp_path):
    #     gas_client = GAS(access_key=accesskey, url=url)
    #     dataset_name = get_dataset_name()
    #     gas_client.create_dataset(dataset_name)
    #     dataset = Dataset(name=dataset_name)
    #     segment = dataset.create_segment("Segment1")
    #     dataset._catalog = Catalog.loads(CATALOG)
    #     path = tmp_path / "sub"
    #     path.mkdir()
    #     for i in range(10):
    #         local_path = path / f"hello{i}.txt"
    #         local_path.write_text(f"CONTENT_{i}")
    #         data = Data(local_path=str(local_path))
    #         data.label = Label.loads(LABEL)
    #         segment.append(data)

    #     dataset_client = gas_client.upload_dataset(dataset)
    #     segment_client = dataset_client.get_segment("Segment1")

    #     segment_client.move_data("hello0.txt", "hello1.txt", strategy="override")

    #     segment_moved = Segment("Segment1", client=dataset_client)
    #     for data in segment_moved:
    #         assert data.path != "hello0.txt"
    #         assert data.label
    #         if data.path == "hello1.txt":
    #             assert data.open().read() == b"CONTENT_0"

    #     gas_client.delete_dataset(dataset_name)

    # @pytest.mark.xfail(__version__ < "1.9.0", reason="not supported until 1.9.0")
    # def test_move_data_skip(self, accesskey, url, tmp_path):
    #     gas_client = GAS(access_key=accesskey, url=url)
    #     dataset_name = get_dataset_name()
    #     gas_client.create_dataset(dataset_name)
    #     dataset = Dataset(name=dataset_name)
    #     segment = dataset.create_segment("Segment1")
    #     dataset._catalog = Catalog.loads(CATALOG)
    #     path = tmp_path / "sub"
    #     path.mkdir()
    #     for i in range(10):
    #         local_path = path / f"hello{i}.txt"
    #         local_path.write_text(f"CONTENT_{i}")
    #         data = Data(local_path=str(local_path))
    #         data.label = Label.loads(LABEL)
    #         segment.append(data)

    #     dataset_client = gas_client.upload_dataset(dataset)
    #     segment_client = dataset_client.get_segment("Segment1")

    #     segment_client.move_data("hello0.txt", "hello1.txt", strategy="skip")

    #     segment_moved = Segment("Segment1", client=dataset_client)
    #     assert segment_moved[0].path == "hello0.txt"
    #     assert segment_moved[1].path == "hello1.txt"
    #     assert segment_moved[0].open().read() == "CONTENT_0"
    #     assert segment_moved[1].open().read() == "CONTENT_1"

    #     gas_client.delete_dataset(dataset_name)


class TestCopy:
    def test_copy_segment(self, accesskey, url, tmp_path):
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
        segment_client = dataset_client.copy_segment("Segment1", "Segment2")
        assert segment_client.name == "Segment2"

        with pytest.raises(InvalidParamsError):
            dataset_client.copy_segment("Segment1", "Segment3", strategy="push")

        segment2 = Segment("Segment2", client=dataset_client)
        assert segment2[0].path == "hello0.txt"
        assert segment2[0].path == segment[0].target_remote_path
        assert segment2[0].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_fusion_segment(self, accesskey, url, tmp_path):
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
        segment_client = dataset_client.copy_segment("Segment1", "Segment2")
        assert segment_client.name == "Segment2"

        with pytest.raises(InvalidParamsError):
            dataset_client.copy_segment("Segment1", "Segment3", strategy="push")

        segment2 = FusionSegment("Segment2", client=dataset_client)
        assert segment2[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert (
            segment2[0][LIDAR_DATA["name"]].path
            == segment[0][LIDAR_DATA["name"]].target_remote_path
        )
        assert segment2[0][LIDAR_DATA["name"]].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_fusion_segment_from_commits(self, accesskey, url, tmp_path):
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
        dataset_client.commit("commit_1")

        dataset_client.create_draft("draft_2")
        dataset_client.commit("commit_2")

        dataset_client.create_draft("draft_3")
        dataset_client_1 = gas_client.get_dataset(dataset_name, is_fusion=True)
        segment_client = dataset_client.copy_segment(
            "Segment1", "Segment2", source_client=dataset_client_1
        )
        assert segment_client.name == "Segment2"

        with pytest.raises(InvalidParamsError):
            dataset_client.copy_segment("Segment1", "Segment3", strategy="push")

        segment2 = FusionSegment("Segment2", client=dataset_client)
        assert segment2[0][LIDAR_DATA["name"]].path == "hello0.txt"
        assert (
            segment2[0][LIDAR_DATA["name"]].path
            == segment[0][LIDAR_DATA["name"]].target_remote_path
        )
        assert segment2[0][LIDAR_DATA["name"]].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_segment_abort(self, accesskey, url, tmp_path):
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
            dataset_client.copy_segment("Segment1", "Segment2")

        gas_client.delete_dataset(dataset_name)

    def test_copy_segment_override(self, accesskey, url, tmp_path):
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
        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment2.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.copy_segment("Segment1", "Segment2", strategy="override")

        segment_copied = Segment("Segment2", client=dataset_client)
        assert segment_copied[0].path == "hello0.txt"
        assert segment_copied[0].path == segment1[0].target_remote_path
        assert segment_copied[0].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_segment_skip(self, accesskey, url, tmp_path):
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
        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment2.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.copy_segment("Segment1", "Segment2", strategy="skip")

        segment_copied = Segment("Segment2", client=dataset_client)
        assert segment_copied[0].path == "hello10.txt"
        assert segment_copied[0].path == segment2[0].target_remote_path
        assert segment_copied[0].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_segment_between_datasets(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = get_dataset_name()
        gas_client.create_dataset(dataset_name_1)
        dataset_1 = Dataset(name=dataset_name_1)
        segment_1 = dataset_1.create_segment("Segment1")
        dataset_1._catalog = Catalog.loads(CATALOG)
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment_1.append(data)
        dataset_client_1 = gas_client.upload_dataset(dataset_1)

        dataset_name_2 = dataset_name_1 + "_2"
        dataset_client_2 = gas_client.create_dataset(dataset_name_2)
        dataset_client_2.create_draft("draft_2")

        segment_client = dataset_client_2.copy_segment(
            "Segment1", "Segment2", source_client=dataset_client_1
        )
        assert segment_client.name == "Segment2"

        segment2 = Segment("Segment2", client=dataset_client_2)
        assert segment2[0].path == "hello0.txt"
        assert segment2[0].path == segment_1[0].target_remote_path
        assert segment2[0].label

        gas_client.delete_dataset(dataset_name_1)
        gas_client.delete_dataset(dataset_name_2)

    def test_copy_segment_from_commits(self, accesskey, url, tmp_path):
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
        dataset_client.commit("commit_1")

        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment.append(data)
        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.commit("commit_2")

        dataset_client_1 = gas_client.get_dataset(dataset_name)
        commit_id = dataset_client_1.list_commits()[-1].commit_id
        dataset_client_1.checkout(revision=commit_id)
        dataset_client.create_draft("draft_3")
        segment_client = dataset_client.copy_segment(
            "Segment1", "Segment2", source_client=dataset_client_1
        )
        assert segment_client.name == "Segment2"

        segment2 = Segment("Segment2", client=dataset_client)
        assert segment2[0].path == "hello0.txt"
        assert segment2[0].path == segment[0].target_remote_path
        assert segment2[0].label
        assert len(segment2) == 10

        gas_client.delete_dataset(dataset_name)

    def test_copy_data(self, accesskey, url, tmp_path):
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
        segment_client = dataset_client.get_segment("Segment1")
        segment_client.copy_data("hello0.txt", "goodbye0.txt")
        segment_client.copy_data("hello1.txt", "hello10.txt")

        with pytest.raises(InvalidParamsError):
            segment_client.copy_data("hello2.txt", "see_you.txt", strategy="push")

        segment2 = Segment("Segment1", client=dataset_client)
        assert segment2[0].path == "goodbye0.txt"
        assert segment2[3].path == "hello10.txt"
        assert segment2[1].label

        gas_client.delete_dataset(dataset_name)

    def test_copy_data_between_datasets(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name_1 = get_dataset_name()
        gas_client.create_dataset(dataset_name_1)
        dataset_1 = Dataset(name=dataset_name_1)
        segment_1 = dataset_1.create_segment("Segment1")
        dataset_1._catalog = Catalog.loads(CATALOG)
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment_1.append(data)
        dataset_client_1 = gas_client.upload_dataset(dataset_1)
        segment_client_1 = dataset_client_1.get_segment("Segment1")

        dataset_name_2 = dataset_name_1 + "_2"
        dataset_client_2 = gas_client.create_dataset(dataset_name_2)
        dataset_client_2.create_draft("draft_2")
        dataset_client_2.create_segment("Segment1")
        segment_client_2 = dataset_client_2.get_segment("Segment1")

        segment_client_2.copy_data("hello0.txt", "hello0.txt", source_client=segment_client_1)

        segment2 = Segment("Segment1", client=dataset_client_2)
        assert segment2[0].path == "hello0.txt"
        assert segment2[0].label

        gas_client.delete_dataset(dataset_name_1)
        gas_client.delete_dataset(dataset_name_2)

    def test_copy_data_from_commits(self, accesskey, url, tmp_path):
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
        dataset_client.commit("commit_1")

        for i in range(10, 20):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment.append(data)
        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.commit("commit_2")

        dataset_client_1 = gas_client.get_dataset(dataset_name)
        commit_id = dataset_client_1.list_commits()[-1].commit_id
        dataset_client_1.checkout(revision=commit_id)
        dataset_client.create_draft("draft_3")
        segment_client_1 = dataset_client_1.get_segment("Segment1")
        segment_client_2 = dataset_client.get_segment("Segment1")
        segment_client_2.copy_data("hello0.txt", "goodbye0.txt", source_client=segment_client_1)

        segment2 = Segment("Segment1", client=dataset_client)
        assert segment2[0].path == "goodbye0.txt"
        assert segment2[0].path != segment[0].target_remote_path
        assert segment2[0].label
        assert len(segment2) == 21

        gas_client.delete_dataset(dataset_name)
