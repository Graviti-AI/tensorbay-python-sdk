#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay import GAS
from tensorbay.dataset import Data, Dataset
from tensorbay.label import Catalog, Label

from .utility import get_dataset_name

MULTI_POLYLINE2D_CATALOG = {
    "isTracking": True,
    "categories": [
        {
            "name": "0",
            "description": "This is an exmaple of test",
        },
        {
            "name": "1",
            "description": "This is an exmaple of test",
        },
    ],
    "attributes": [
        {"name": "gender", "enum": ["male", "female"]},
        {"name": "occluded", "type": "integer", "minimum": 1, "maximum": 5},
    ],
}
CATALOG_CONTENTS = {
    "MULTI_POLYLINE2D": MULTI_POLYLINE2D_CATALOG,
}

MULTI_POLYLINE2D_LABEL = [
    {
        "category": "cat",
        "attributes": {"gender": "male"},
        "instance": "12345",
        "multiPolyline2d": [
            [{"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 2}],
            [{"x": 2, "y": 3}, {"x": 3, "y": 5}],
        ],
    }
]
LABEL = {
    "MULTI_POLYLINE2D": MULTI_POLYLINE2D_LABEL,
}


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

        gas_client.delete_dataset(dataset_name)
