#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestDatasetClient"""

import pytest

from tensorbay.client import GAS, GASResponseError, GASSegmentError
from tensorbay.dataset import Data, Frame, FusionSegment, Segment
from tensorbay.label import Catalog, Label
from tensorbay.sensor import Sensor

from .utility import get_draft_number_by_title, get_random_dataset_name

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


class TestDatasetClient:
    """Test DatasetClient class."""

    def test_create_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        draft_number_1 = dataset_client.create_draft("draft-1")
        assert draft_number_1 == 1
        assert dataset_client.status.is_draft
        assert dataset_client.status.draft_number == draft_number_1
        assert dataset_client.status.commit_id is None
        with pytest.raises(TypeError):
            dataset_client.create_draft("draft-2")
        draft_number = get_draft_number_by_title(
            dataset_client.list_draft_titles_and_numbers(), "draft-1"
        )
        assert draft_number_1 == draft_number

        gas_client.delete_dataset(dataset_name)

    def test_list_drafts(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit(message="commit-draft-1")
        draft_number_2 = dataset_client.create_draft("draft-2")

        # After committing, the draft will be deleted
        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_draft_titles_and_numbers(), "draft-1")
        draft_number = get_draft_number_by_title(
            dataset_client.list_draft_titles_and_numbers(), "draft-2"
        )
        assert draft_number_2 == draft_number
        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_draft_titles_and_numbers(), "draft-3")

        gas_client.delete_dataset(dataset_name)

    def test_commit_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1")
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", tag="V1")

        dataset_client.create_draft("draft-3")
        with pytest.raises(GASResponseError):
            dataset_client.commit("commit-3", tag="V1")
        dataset_client.commit("commit-3", tag="V2")
        assert not dataset_client.status.is_draft
        assert dataset_client.status.draft_number is None
        assert dataset_client.status.commit_id is not None
        # After committing, the draft will be deleted
        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_draft_titles_and_numbers(), "draft-3")

        gas_client.delete_dataset(dataset_name)

    def test_create_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(TypeError):
            dataset_client.get_or_create_segment("segment")
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment")
        assert segment_client.status.is_draft
        assert segment_client.name == "segment"
        dataset_client.get_segment("segment")

        gas_client.delete_dataset(dataset_name)

    def test_create_fusion_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)

        with pytest.raises(TypeError):
            dataset_client.get_or_create_segment("segment")
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment")
        assert segment_client.status.is_draft
        assert segment_client.name == "segment"
        dataset_client.get_segment("segment")

        gas_client.delete_dataset(dataset_name)

    def test_list_segment_names(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.get_or_create_segment("segment1")
        dataset_client.get_or_create_segment("segment2")

        segments = list(dataset_client.list_segment_names())
        assert "segment1" in segments
        assert "segment2" in segments
        assert "segment3" not in segments

        gas_client.delete_dataset(dataset_name)

    def test_catalog(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(TypeError):
            dataset_client.upload_catalog(Catalog.loads(CATALOG))
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        catalog = dataset_client.get_catalog()
        # todo: match the input and output catalog

        gas_client.delete_dataset(dataset_name)

    def test_delete_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.get_or_create_segment("segment1")

        dataset_client.delete_segment("segment1")
        with pytest.raises(GASSegmentError):
            dataset_client.get_segment("segment1")

        gas_client.delete_dataset(dataset_name)

    def test_get_and_upload_segment_with_no_file(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("test")

        segment = Segment("segment1")

        dataset_client.upload_segment(segment)
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 0

        gas_client.delete_dataset(dataset_name)

    def test_get_and_upload_segment_only_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_get_and_upload_segment_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_get_and_upload_fusion_segment_with_no_file(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")

        segment = FusionSegment("segment1")

        dataset_client.upload_segment(segment)
        segment1 = FusionSegment(name="segment1", client=dataset_client)
        assert len(segment1) == 0
        assert not segment1.sensors

        gas_client.delete_dataset(dataset_name)

    def test_get_and_upload_fusion_segment_only_with_file(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_get_and_upload_fusion_segment_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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

    def test_draft_and_top_commit_inherit(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_random_dataset_name()
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
        dataset_client.commit("commit-1")
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].get_url()
        assert segment1[0].path == segment[0].target_remote_path

        dataset_client.create_draft("draft-2")
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].get_url()
        assert segment1[0].path == segment[0].target_remote_path

        gas_client.delete_dataset(dataset_name)
