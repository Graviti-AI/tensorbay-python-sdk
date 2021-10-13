#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import numpy as np
import pytest

from tensorbay import GAS
from tensorbay.client.statistics import Statistics
from tensorbay.dataset import Data, Dataset
from tensorbay.label import Catalog, InstanceMask, Label, PanopticMask, SemanticMask
from tensorbay.label.label_mask import RemoteInstanceMask, RemotePanopticMask, RemoteSemanticMask
from tests.utility import get_dataset_name

CATALOG_ATTRBUTES = [
    {"name": "gender", "enum": ["male", "female"]},
    {"name": "occluded", "type": "integer", "minimum": 1, "maximum": 5},
]
GEOMETRY_CATALOG = {
    "isTracking": True,
    "categories": [
        {
            "name": "0",
            "description": "This is an example of test",
        },
        {
            "name": "1",
            "description": "This is an example of test",
        },
    ],
    "attributes": CATALOG_ATTRBUTES,
}
MASK_CATALOG_CONTENTS = {
    "categories": [
        {"name": "cat", "description": "This is an exmaple of test", "categoryId": 0},
        {"name": "dog", "description": "This is an exmaple of test", "categoryId": 1},
    ],
    "attributes": CATALOG_ATTRBUTES,
}
CATALOG_CONTENTS = {
    "MULTI_POLYLINE2D": GEOMETRY_CATALOG,
    "MULTI_POLYGON": GEOMETRY_CATALOG,
    "RLE": GEOMETRY_CATALOG,
    "SEMANTIC_MASK": MASK_CATALOG_CONTENTS,
    "INSTANCE_MASK": MASK_CATALOG_CONTENTS,
    "PANOPTIC_MASK": MASK_CATALOG_CONTENTS,
}


COMMON_LABEL = {
    "category": "cat",
    "attributes": {"gender": "male"},
    "instance": "12345",
}
MULTI_POLYLINE2D_LABEL = [
    {
        **COMMON_LABEL,
        "multiPolyline2d": [
            [{"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 2}],
            [{"x": 2, "y": 3}, {"x": 3, "y": 5}],
        ],
    }
]
MULTI_POLYGON_LABEL = [
    {
        **COMMON_LABEL,
        "multiPolygon": [
            [
                {"x": 1.0, "y": 2.0},
                {"x": 2.0, "y": 3.0},
                {"x": 1.0, "y": 3.0},
            ],
            [{"x": 1.0, "y": 4.0}, {"x": 2.0, "y": 3.0}, {"x": 1.0, "y": 8.0}],
        ],
    }
]
RLE_LABEL = [
    {
        **COMMON_LABEL,
        "rle": [272, 2, 4, 4, 2, 9],
    }
]
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

LABEL = {
    "MULTI_POLYLINE2D": MULTI_POLYLINE2D_LABEL,
    "MULTI_POLYGON": MULTI_POLYGON_LABEL,
    "RLE": RLE_LABEL,
}
STATISTICS = {
    "MULTI_POLYGON": {
        "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
        "categories": [
            {
                "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
                "name": "cat",
                "quantity": 1,
            }
        ],
        "quantity": 1,
    },
    "MULTI_POLYLINE2D": {
        "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
        "categories": [
            {
                "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
                "name": "cat",
                "quantity": 1,
            }
        ],
        "quantity": 1,
    },
    "RLE": {
        "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
        "categories": [
            {
                "attributes": [{"enum": ["male"], "name": "gender", "quantities": [1]}],
                "name": "cat",
                "quantity": 1,
            }
        ],
        "quantity": 1,
    },
}
TOTALSIZE = 7


@pytest.fixture
def mask_file(tmp_path):
    local_path = tmp_path / "hello.png"
    mask = np.random.randint(0, 1, 48).reshape(8, 6)
    mask.dump(local_path)
    return local_path


class TestUploadLabel:
    def test_upload_dataset_with_label(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        # When uploading label, upload catalog first.
        dataset._catalog = Catalog.loads(CATALOG_CONTENTS)

        path = tmp_path / "sub"
        path.mkdir()
        local_path = path / "hello.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        data.label = Label.loads(LABEL)
        segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.commit("upload dataset with label")
        dataset = Dataset(dataset_name, gas_client)
        assert dataset.catalog == Catalog.loads(CATALOG_CONTENTS)
        assert dataset[0][0].label == Label.loads(LABEL)

        statistics1 = dataset_client.get_label_statistics()
        assert statistics1 == Statistics(STATISTICS)

        total_size = dataset_client.get_total_size()
        assert total_size == TOTALSIZE
        gas_client.delete_dataset(dataset_name)

    def test_upload_dataset_with_mask(self, accesskey, url, tmp_path, mask_file):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        # When uploading label, upload catalog first.
        dataset._catalog = Catalog.loads(CATALOG_CONTENTS)

        path = tmp_path / "sub"
        path.mkdir()
        local_path = path / "hello.txt"
        local_path.write_text("CONTENT")
        data = Data(local_path=str(local_path))
        remote_semantic_mask = SemanticMask(str(mask_file))
        remote_semantic_mask.all_attributes = {0: {"occluded": True}, 1: {"occluded": False}}
        data.label.semantic_mask = remote_semantic_mask

        instance_mask = InstanceMask(str(mask_file))
        instance_mask.all_attributes = {0: {"occluded": True}, 1: {"occluded": False}}
        data.label.instance_mask = instance_mask

        panoptic_mask = PanopticMask(str(mask_file))
        panoptic_mask.all_category_ids = {100: 0, 101: 1}
        data.label.panoptic_mask = panoptic_mask
        segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        dataset_client.commit("upload dataset with label")
        dataset = Dataset(dataset_name, gas_client)
        remote_semantic_mask = dataset[0][0].label.semantic_mask
        semantic_mask = RemoteSemanticMask.from_response_body(SEMANTIC_MASK_LABEL)
        assert dataset.catalog == Catalog.loads(CATALOG_CONTENTS)
        assert remote_semantic_mask.path == semantic_mask.path
        assert remote_semantic_mask.all_attributes == semantic_mask.all_attributes

        remote_instance_mask = dataset[0][0].label.instance_mask
        instance_mask = RemoteInstanceMask.from_response_body(INSTANCE_MASK_LABEL)
        assert dataset.catalog == Catalog.loads(CATALOG_CONTENTS)
        assert remote_instance_mask.path == instance_mask.path
        assert remote_instance_mask.all_attributes == instance_mask.all_attributes

        remote_panoptic_mask = dataset[0][0].label.panoptic_mask
        panoptic_mask = RemotePanopticMask.from_response_body(PANOPTIC_MASK_LABEL)
        assert dataset.catalog == Catalog.loads(CATALOG_CONTENTS)
        assert remote_panoptic_mask.path == panoptic_mask.path
        assert remote_panoptic_mask.all_category_ids == panoptic_mask.all_category_ids

        gas_client.delete_dataset(dataset_name)
