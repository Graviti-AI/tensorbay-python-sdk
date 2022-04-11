#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os

import pytest

from tensorbay.client import GAS
from tensorbay.dataset import Data, Frame, FusionDataset
from tensorbay.geometry import Vector3D
from tensorbay.label import Catalog, Label
from tensorbay.sensor import Camera
from tests.utility import get_dataset_name

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
            {"name": "attribute_1", "type": "boolean"},
            {"name": "attribute_2", "type": "integer", "minimum": 0},
        ],
    }
}

LABEL_1 = {
    "BOX2D": [
        {
            "category": "01",
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
            "attributes": {"attribute_1": True, "attribute_2": 3},
        }
    ]
}
LABEL_2 = {
    "BOX2D": [
        {
            "category": "02",
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
            "attributes": {"attribute_1": False, "attribute_2": 1},
        }
    ]
}
LABEL = {"CAM_BACK_RIGHT": LABEL_1, "CAM_BACK_LEFT": LABEL_2}

SEGMENTS_NAME = ("test", "train")
CAMERAS_NAME = ("CAM_BACK_RIGHT", "CAM_BACK_LEFT")


@pytest.fixture(scope="class", name="dataset_client")
def init_dataset_client(accesskey, url, tmp_path_factory):
    gas_client = GAS(access_key=accesskey, url=url)
    dataset_name = get_dataset_name()
    gas_client.create_dataset(dataset_name, is_fusion=True)

    dataset = FusionDataset(name=dataset_name)
    dataset._catalog = Catalog.loads(CATALOG)
    path = tmp_path_factory.mktemp("sub")
    os.makedirs(path, exist_ok=True)
    for segment_name in SEGMENTS_NAME:
        segment = dataset.create_segment(segment_name)
        frame = Frame()
        for camera_name, label in LABEL.items():
            camera = Camera(camera_name)
            translation = Vector3D(1, 2, 3)
            camera.set_extrinsics(translation=translation)
            camera.set_extrinsics(translation=translation)
            camera.set_camera_matrix(fx=1.1, fy=1.1, cx=1.1, cy=1.1)
            camera.set_distortion_coefficients(p1=1.2, p2=1.2, k1=1.2, k2=1.2)
            segment.sensors.add(camera)
            local_path = path / f"{segment_name}_{camera_name}.txt"
            local_path.write_text(f"CONTENT_{segment_name}_{camera_name}")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(label)
            frame[camera_name] = data
        segment.append(frame)
    dataset_client = gas_client.upload_dataset(dataset)
    dataset_client.commit("commit-1")

    yield dataset_client

    gas_client.delete_dataset(dataset_name)


@pytest.fixture(scope="class", name="job")
def init_job(dataset_client):
    job = dataset_client.basic_search.create_job(
        title="basic search job example",
        conjunction="and",
        unit="file",
        filters=[("withLabel", "=", True)],
    )
    job.abort()
    job.update()
    assert job.status == "ABORTED"

    job = dataset_client.basic_search.create_job(
        title="basic search job example",
        description="search description",
        conjunction="and",
        unit="file",
        filters=[
            (
                "category",
                "in",
                ["01", "02"],
                "BOX2D",
            ),
            ("size", ">", 0),
            ("withLabel", "=", True),
            ("attribute", "in", {"attribute_1": [True, False], "attribute_2": [3]}, "BOX2D"),
            ("segment", "in", ["test"]),
            ("sensor", "in", ["CAM_BACK_RIGHT"]),
        ],
    )

    yield job


class TestBasicSearch:
    @pytest.mark.xfail(reason="there are still some bugs in creating and aborting job")
    def test_get_job(self, dataset_client, job):
        job_id = job.job_id
        job = dataset_client.basic_search.get_job(job_id)
        assert job.job_id == job_id

    @pytest.mark.xfail(reason="there are still some bugs in creating and aborting job")
    def test_update_job(self, job):
        job.update(until_complete=True)
        assert job.status == "SUCCESS"

    @pytest.mark.xfail(reason="there are still some bugs in creating and aborting job")
    def test_create_dataset(self, accesskey, url, dataset_client, job):
        job.update()
        job.create_dataset("search_dataset")
        gas_client = GAS(access_key=accesskey, url=url)

        search_dataset = gas_client.get_dataset("search_dataset", True)

        search_dataset_segment = search_dataset.get_or_create_segment("test")
        assert (
            search_dataset_segment.get_sensors() == dataset_client.get_segment("test").get_sensors()
        )

        search_dataset_frames = search_dataset_segment.list_frames()
        assert len(search_dataset_frames) == 1
        search_dataset_data = search_dataset_frames[0]["CAM_BACK_RIGHT"]
        assert search_dataset_data.path == "test_CAM_BACK_RIGHT.txt"
        assert search_dataset_data.label == Label.loads(LABEL_1)

    @pytest.mark.xfail(reason="there are still some bugs in creating and aborting job")
    def test_job_result(self, dataset_client, job):
        job.update()
        fusion_search_result = job.result

        search_result_segment_names = fusion_search_result.list_segment_names()
        assert len(search_result_segment_names) == 1

        assert search_result_segment_names[0] == "test"

        search_result_frames = fusion_search_result.list_frames("test")
        assert len(search_result_frames) == 1
        search_result_data = search_result_frames[0]["CAM_BACK_RIGHT"]
        assert search_result_data.path == "test_CAM_BACK_RIGHT.txt"
        assert search_result_data.label == Label.loads(LABEL_1)

        search_result_sensors = fusion_search_result.get_sensors("test")
        assert search_result_sensors == dataset_client.get_segment("test").get_sensors()

        assert fusion_search_result.get_label_statistics().dumps() == {
            "BOX2D": {
                "attributes": [{"enum": [True], "name": "attribute_1", "quantities": [1]}],
                "categories": [
                    {
                        "attributes": [{"enum": [True], "name": "attribute_1", "quantities": [1]}],
                        "name": "01",
                        "quantity": 1,
                    }
                ],
                "quantity": 1,
            }
        }

    @pytest.mark.xfail(reason="there are still some bugs in creating and aborting job")
    def test_list_jobs(self, dataset_client):
        jobs = dataset_client.basic_search.list_jobs()
        assert len(jobs) == 2
        for job in jobs:
            dataset_client.basic_search.delete_job(job.job_id)
        jobs = dataset_client.basic_search.list_jobs()
        assert len(jobs) == 0
