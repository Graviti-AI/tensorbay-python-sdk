#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestVector"""

import pytest

from ...label import Classification
from ..data import Data, Label, RemoteData

_LABEL_DATA = [
    {"CLASSIFICATION": {"category": "test_categoty", "attributes": {"test_attribute1": "a"}}},
    {
        "BOX2D": [
            {
                "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
                "category": "test_categoty",
                "attributes": {"test_attribute1": "a"},
            }
        ]
    },
    {
        "BOX3D": [
            {
                "box3d": {
                    "translation": {"x": 1, "y": 1, "z": 1},
                    "rotation": {"w": 1, "x": 1, "y": 1, "z": 1},
                    "size": {"x": 1, "y": 1, "z": 1},
                },
                "category": "test_categoty",
                "attributes": {"test_attribute1": "a"},
            }
        ]
    },
    {
        "POLYGON2D": [
            {
                "polygon2d": [{"x": 1, "y": 1}, {"x": 2, "y": 2}, {"x": 1, "y": 2}],
                "category": "test_categoty",
                "attributes": {"test_attribute1": "a"},
            }
        ]
    },
    {
        "POLYLINE2D": [
            {
                "polyline2d": [{"x": 1, "y": 1}, {"x": 2, "y": 2}, {"x": 1, "y": 2}],
                "category": "test_categoty",
                "attributes": {"test_attribute1": "a"},
            }
        ]
    },
    {
        "KEYPOINTS2D": [
            {
                "keypoints2d": [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
                "category": "test_categoty",
                "attributes": {"test_attribute1": "a"},
            }
        ]
    },
    {
        "SENTENCE": [{"sentence": [{"text": "she"}, {"text": "like"}, {"text": "cat"}]}],
    },
]

_DATA = {"localPath": "test.json", "timestamp": 1614667532}
_REMOTE_DATA = {"remotePath": "test.json", "timestamp": 1614667532}


class TestLabel:
    """Test Labels class."""

    def test_bool(self) -> None:
        labels = Label()
        assert bool(labels) == False

        labels.classification = Classification()
        assert bool(labels) == True

    @pytest.mark.parametrize("loads", _LABEL_DATA)
    def test_loads_dumps(self, loads) -> None:
        labels = Label.loads(loads)
        assert labels.dumps() == loads


class TestData:
    """Test Data class."""

    def test_init(self) -> None:
        local_path = "test.json"
        target_remote_path = "A/test.json"
        timestamp = 1614667532

        data = Data(local_path, target_remote_path=target_remote_path, timestamp=timestamp)
        assert data.path == local_path
        assert data.target_remote_path == target_remote_path
        assert data.timestamp == timestamp

    def test_loads_dumps(self) -> None:
        data = Data.loads(_DATA)
        assert data.dumps() == _DATA

    def test_target_remote_path(self) -> None:
        target_remote_path = "test2.json"
        data_object = Data("test.json")
        data_object.target_remote_path = target_remote_path
        assert data_object.target_remote_path == target_remote_path


class TestRemoteData:
    """Test RemoteData class."""

    def test_init(self) -> None:
        remote_path = "A/test.json"
        timestamp = 1614667532
        remote_data = RemoteData(remote_path, timestamp=timestamp, url_getter=lambda x: x)
        assert remote_data.path == remote_path
        assert remote_data.timestamp == timestamp
        assert remote_data.get_url() == remote_path

    def test_get_url(self) -> None:
        remote_data = RemoteData("A/test.josn")
        with pytest.raises(ValueError):
            remote_data.get_url()
