#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class TestVector"""

import pytest

from ...label import Classification
from ..data import Data, Labels

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

_DATA = {"fileuri": "test.json", "timestamp": 20201023}


@pytest.fixture
def data_object():
    return Data("test.json")


class TestLabels:
    """Test Labels class."""

    def test_bool(self) -> None:
        labels = Labels()
        assert bool(labels) == False

        labels.classification = Classification()
        assert bool(labels) == True

    @pytest.mark.parametrize("loads", _LABEL_DATA)
    def test_loads_dumps(self, loads) -> None:
        labels = Labels.loads(loads)
        assert labels.dumps() == loads


class TestData:
    """Test Data class."""

    def test_loads_dumps(self) -> None:
        data = Data.loads(_DATA)
        assert data.dumps() == _DATA

    def test_get_url(self, data_object) -> None:
        with pytest.raises(ValueError):
            data_object.get_url()

    def test_get_tbrn(self, data_object) -> None:
        with pytest.raises(ValueError):
            data_object.tbrn

    def test_remote_path(self, data_object) -> None:
        assert data_object.remote_path == "test.json"

        data_object.remote_path = "test2.json"
        assert data_object.remote_path == "test2.json"

    def test_local_path(self, data_object) -> None:
        assert data_object.local_path == "test.json"

        data_object = Data.loads({"fileuri": "tb:datasetname:segmentname://test.json"})
        assert data_object.local_path == ""
