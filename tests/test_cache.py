#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay import GAS
from tensorbay.dataset import Data, Dataset, Frame, FusionSegment, Segment
from tensorbay.label import Catalog, InstanceMask, Label, SemanticMask
from tensorbay.sensor import Sensors
from tests.utility import get_dataset_name

_CATALOG = {
    "BOX2D": {
        "categories": [
            {"name": "01"},
            {"name": "02"},
            {"name": "03"},
            {"name": "04"},
            {"name": "05"},
        ]
    },
    "SEMANTIC_MASK": {
        "categories": [
            {"name": "01", "categoryId": 1},
            {"name": "02", "categoryId": 2},
            {"name": "03", "categoryId": 3},
            {"name": "04", "categoryId": 4},
            {"name": "05", "categoryId": 5},
        ]
    },
    "INSTANCE_MASK": {},
}

_LABEL = {
    "BOX2D": [
        {
            "category": "01",
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}

_SENSORS_DATA = [
    {
        "name": "Lidar1",
        "type": "LIDAR",
        "extrinsics": {
            "translation": {"x": 1, "y": 2, "z": 3},
            "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
        },
    },
    {
        "name": "Camera1",
        "type": "CAMERA",
        "extrinsics": {
            "translation": {"x": 2, "y": 3, "z": 4},
            "rotation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        },
        "intrinsics": {
            "cameraMatrix": {"fx": 1, "fy": 2, "cx": 3, "cy": 4, "skew": 5},
        },
    },
]

_SEGMENT_LENGTH = 5


class TestCache:
    def test_cache_dataset(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        # When uploading label, upload catalog first.
        dataset._catalog = Catalog.loads(_CATALOG)

        path = tmp_path / "sub"
        semantic_path = tmp_path / "semantic_mask"
        instance_path = tmp_path / "instance_mask"
        path.mkdir()
        semantic_path.mkdir()
        instance_path.mkdir()
        for i in range(_SEGMENT_LENGTH):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(_LABEL)

            semantic_mask = semantic_path / f"semantic_mask{i}.png"
            semantic_mask.write_text("SEMANTIC_MASK")
            data.label.semantic_mask = SemanticMask(str(semantic_mask))

            instance_mask = instance_path / f"instance_mask{i}.png"
            instance_mask.write_text("INSTANCE_MASK")
            data.label.instance_mask = InstanceMask(str(instance_mask))
            segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.commit("commit-1")
        cache_path = tmp_path / "cache_test"
        dataset_client.enable_cache(str(cache_path))
        segment1 = Segment("Segment1", client=dataset_client)
        for data in segment1:
            data.open()
            data.label.semantic_mask.open()
            data.label.instance_mask.open()

        segment_cache_path = (
            cache_path / dataset_client.dataset_id / dataset_client.status.commit_id / "Segment1"
        )
        semantic_mask_cache_path = segment_cache_path / "semantic_mask"
        instance_mask_cache_path = segment_cache_path / "instance_mask"

        for cache_dir, extension in (
            (segment_cache_path, "txt"),
            (semantic_mask_cache_path, "png"),
            (instance_mask_cache_path, "png"),
        ):
            assert set(cache_dir.glob(f"*.{extension}")) == {
                cache_dir / f"hello{i}.{extension}" for i in range(_SEGMENT_LENGTH)
            }

        gas_client.delete_dataset(dataset_name)

    def test_cache_fusion_dataset(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)
        dataset_client.create_draft("draft-1")

        segment = FusionSegment("Segment1")
        segment.sensors = Sensors.loads(_SENSORS_DATA)

        paths = {"Lidar1": tmp_path / "lidar", "Camera1": tmp_path / "camera"}
        for path in paths.values():
            path.mkdir()

        for i in range(_SEGMENT_LENGTH):
            frame = Frame()
            for sensor_data in _SENSORS_DATA:
                sensor_name = sensor_data["name"]
                data_path = paths[sensor_name] / f"{sensor_name}{i}.txt"
                data_path.write_text("CONTENT")
                frame[sensor_name] = Data(local_path=str(data_path))
            segment.append(frame)

        dataset_client.upload_segment(segment)
        dataset_client.commit("commit-1")
        cache_path = tmp_path / "cache_test"
        dataset_client.enable_cache(str(cache_path))
        segment1 = FusionSegment(name="Segment1", client=dataset_client)
        for frame in segment1:
            for data in frame.values():
                data.open()

        segment_cache_path = (
            cache_path / dataset_client.dataset_id / dataset_client.status.commit_id / "Segment1"
        )
        correct_files = {
            segment_cache_path / f'{sensor_data["name"]}{i}.txt'
            for i in range(_SEGMENT_LENGTH)
            for sensor_data in _SENSORS_DATA
        }
        assert set(segment_cache_path.glob("*.txt")) == correct_files

        gas_client.delete_dataset(dataset_name)
