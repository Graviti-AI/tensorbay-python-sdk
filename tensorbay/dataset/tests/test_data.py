#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...label import Classification, LabeledBox2D
from ..data import Data, Label, RemoteData

_FAILED_DATA = {
    "box2d": [
        {
            "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
        }
    ]
}
_CLASSIFICATION_DATA = {
    "CLASSIFICATION": {"category": "test_categoty", "attributes": {"test_attribute1": "a"}}
}
_BOX2D_DATA = {
    "BOX2D": [
        {
            "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
            "category": "test_categoty",
            "attributes": {"test_attribute1": "a"},
        }
    ]
}

_DATA = {"localPath": "test.json", "timestamp": 1614667532, "label": {}}
_REMOTE_DATA = {"remotePath": "test.json", "timestamp": 1614667532, "label": {}}


class TestLabel:
    def test_bool(self):
        label = Label()
        assert bool(label) == False

        label.classification = Classification()
        assert bool(label) == True

    def test_loads(self):
        label = Label.loads(_FAILED_DATA)
        assert hasattr(label, "box2d") == False

        label = Label.loads(_CLASSIFICATION_DATA)
        assert label.classification.category == _CLASSIFICATION_DATA["CLASSIFICATION"]["category"]
        assert (
            label.classification.attributes == _CLASSIFICATION_DATA["CLASSIFICATION"]["attributes"]
        )

        label = Label.loads(_BOX2D_DATA)
        box2d_object = label.box2d[0]
        box2d = _BOX2D_DATA["BOX2D"][0]
        assert box2d_object.category == box2d["category"]
        assert box2d_object.attributes == box2d["attributes"]
        assert box2d_object._data == (1, 1, 2, 2)

    def test_dumps(self):
        category = "test_categoty"
        attributes = {"test_attribute1": "a"}
        label = Label()
        label.classification = Classification(category, attributes)
        assert label.dumps() == _CLASSIFICATION_DATA

        label = Label()
        label.box2d = [LabeledBox2D(1, 1, 2, 2, category=category, attributes=attributes)]
        assert label.dumps() == _BOX2D_DATA


class TestData:
    def test_init(self):
        local_path = "test.json"
        target_remote_path = "A/test.json"
        timestamp = 1614667532

        data = Data(local_path, target_remote_path=target_remote_path, timestamp=timestamp)
        assert data.path == local_path
        assert data.target_remote_path == target_remote_path
        assert data.timestamp == timestamp

    def test_loads(self):
        data = Data.loads(_DATA)
        assert data.path == _DATA["localPath"]
        assert data.timestamp == _DATA["timestamp"]

    def test_dumps(self):
        data = Data("test.json", timestamp=_DATA["timestamp"])
        assert data.dumps() == _DATA

    def test_target_remote_path(self):
        target_remote_path = "test2.json"
        data_object = Data("test.json")
        data_object.target_remote_path = target_remote_path
        assert data_object.target_remote_path == target_remote_path


class TestRemoteData:
    def test_init(self):
        remote_path = "A/test.json"
        timestamp = 1614667532
        remote_data = RemoteData(remote_path, timestamp=timestamp, url_getter=lambda x: x)
        assert remote_data.path == remote_path
        assert remote_data.timestamp == timestamp
        assert remote_data.get_url() == remote_path

    def test_get_url(self):
        remote_data = RemoteData("A/test.josn")
        with pytest.raises(ValueError):
            remote_data.get_url()

    def test_loads(self):
        data = RemoteData.loads(_REMOTE_DATA)
        assert data.path == _REMOTE_DATA["remotePath"]
        assert data.timestamp == _REMOTE_DATA["timestamp"]

    def test_dumps(self):
        data = RemoteData("test.json", timestamp=_DATA["timestamp"])
        assert data.dumps() == _REMOTE_DATA
