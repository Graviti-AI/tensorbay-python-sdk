#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import Polygon, Vector2D
from .. import (
    LabeledMultiPolygon,
    LabeledPolygon,
    LabeledRLE,
    MultiPolygonSubcatalog,
    PolygonSubcatalog,
    RLESubcatalog,
)

_DATA_LABELEDMULTIPOLYGON = {
    "multiPolygon": [
        [
            {"x": 1.0, "y": 2.0},
            {"x": 2.0, "y": 3.0},
            {"x": 1.0, "y": 3.0},
        ],
        [{"x": 1.0, "y": 4.0}, {"x": 2.0, "y": 3.0}, {"x": 1.0, "y": 8.0}],
    ],
    "category": "example",
    "attributes": {"key": "value"},
    "instance": "123",
}
_DATA_LABELEDRLE = {
    "rle": [272, 2, 4, 4, 2, 9],
    "category": "example",
    "attributes": {"key": "value"},
    "instance": "123",
}


@pytest.fixture
def subcatalog_polygon(is_tracking_data, categories_catalog_data, attributes_catalog_data):
    return {
        "isTracking": is_tracking_data,
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
    }


class TestLabeledPolygon:
    def test_init(self):
        labeledpolygon = LabeledPolygon(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolygon[0] == Vector2D(1, 2)
        assert labeledpolygon.category == "cat"
        assert labeledpolygon.attributes == {"gender": "male"}
        assert labeledpolygon.instance == "12345"

    def test_eq(self):
        polygon1 = LabeledPolygon([[1, 1], [1, 2]], category="cat", attributes={"gender": "male"})
        polygon2 = LabeledPolygon([[1, 1], [1, 2]], category="cat", attributes={"gender": "male"})
        polygon3 = LabeledPolygon([[1, 1], [1, 3]], category="cat", attributes={"gender": "male"})

        assert polygon1 == polygon2
        assert polygon1 != polygon3

    def test_loads(self):
        content = {
            "polygon": [
                {"x": 1, "y": 2},
            ],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }
        labeledpolygon = LabeledPolygon.loads(content)

        assert labeledpolygon[0] == Vector2D(1, 2)
        assert labeledpolygon.category == "cat"
        assert labeledpolygon.attributes == {"gender": "male"}
        assert labeledpolygon.instance == 12345

    def test_dumps(self):
        labeledpolygon = LabeledPolygon(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolygon.dumps() == {
            "polygon": [
                {"x": 1, "y": 2},
            ],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": "12345",
        }


class TestPolygonSubcatalog:
    def test_init(self, is_tracking_data):
        polygon_subcatalog = PolygonSubcatalog(is_tracking_data)
        polygon_subcatalog.is_tracking = is_tracking_data

    def test_eq(self):
        content1 = {
            "isTracking": True,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        content2 = {
            "isTracking": False,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        polygon_subcatalog1 = PolygonSubcatalog.loads(content1)
        polygon_subcatalog2 = PolygonSubcatalog.loads(content1)
        polygon_subcatalog3 = PolygonSubcatalog.loads(content2)

        assert polygon_subcatalog1 == polygon_subcatalog2
        assert polygon_subcatalog1 != polygon_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_polygon):
        subcatalog = PolygonSubcatalog.loads(subcatalog_polygon)

        assert subcatalog.is_tracking == subcatalog_polygon["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes, subcatalog_polygon):
        subcatalog = PolygonSubcatalog()
        subcatalog.is_tracking = subcatalog_polygon["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes

        # isTracking will not dumps out when isTracking is false
        if not subcatalog_polygon["isTracking"]:
            del subcatalog_polygon["isTracking"]

        assert subcatalog.dumps() == subcatalog_polygon


class TestLabeledMultiPolygon:
    def test_init(self):
        labeledmultipolygon = LabeledMultiPolygon(
            [[(1.0, 2.0), (2.0, 3.0), (1.0, 3.0)], [(1.0, 4.0), (2.0, 3.0), (1.0, 8.0)]],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )
        assert labeledmultipolygon[0] == Polygon([(1.0, 2.0), (2.0, 3.0), (1.0, 3.0)])
        assert labeledmultipolygon.category == "example"
        assert labeledmultipolygon.attributes == {"key": "value"}
        assert labeledmultipolygon.instance == "123"

    def test_loads(self):
        labeledmultipolygon = LabeledMultiPolygon.loads(_DATA_LABELEDMULTIPOLYGON)
        assert labeledmultipolygon == LabeledMultiPolygon(
            [[(1.0, 2.0), (2.0, 3.0), (1.0, 3.0)], [(1.0, 4.0), (2.0, 3.0), (1.0, 8.0)]],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )

    def test_dumps(self):
        labeledmultipolygon = LabeledMultiPolygon(
            [[(1.0, 2.0), (2.0, 3.0), (1.0, 3.0)], [(1.0, 4.0), (2.0, 3.0), (1.0, 8.0)]],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )
        assert labeledmultipolygon.dumps() == _DATA_LABELEDMULTIPOLYGON


class TestMultiPolygonSubcatalog:
    def test_init(self, is_tracking_data):
        multi_polygon_subcatalog = MultiPolygonSubcatalog(is_tracking_data)
        assert multi_polygon_subcatalog.is_tracking == is_tracking_data

    def test_eq(self):
        contents1 = {
            "isTracking": True,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        contents2 = {
            "isTracking": False,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        multi_polygon_subcatalog1 = MultiPolygonSubcatalog.loads(contents1)
        multi_polygon_subcatalog2 = MultiPolygonSubcatalog.loads(contents1)
        multi_polygon_subcatalog3 = MultiPolygonSubcatalog.loads(contents2)

        assert multi_polygon_subcatalog1 == multi_polygon_subcatalog2
        assert multi_polygon_subcatalog1 != multi_polygon_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_polygon):
        subcatalog = MultiPolygonSubcatalog.loads(subcatalog_polygon)

        assert subcatalog.is_tracking == subcatalog_polygon["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes, subcatalog_polygon):
        subcatalog = MultiPolygonSubcatalog()
        subcatalog.is_tracking = subcatalog_polygon["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes

        # isTracking will not dump out when isTracking is false
        if not subcatalog_polygon["isTracking"]:
            del subcatalog_polygon["isTracking"]

        assert subcatalog.dumps() == subcatalog_polygon


class TestLabeledRLE:
    def test_init(self):
        labeled_rle = LabeledRLE(
            [272, 2, 4, 4, 2, 9],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )
        assert labeled_rle._data == [272, 2, 4, 4, 2, 9]
        assert labeled_rle.category == "example"
        assert labeled_rle.attributes == {"key": "value"}
        assert labeled_rle.instance == "123"

    def test_loads(self):
        labeled_rle = LabeledRLE.loads(_DATA_LABELEDRLE)
        assert labeled_rle == LabeledRLE(
            [272, 2, 4, 4, 2, 9],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )

    def test_dumps(self):
        labeled_rle = LabeledRLE(
            [272, 2, 4, 4, 2, 9],
            category="example",
            attributes={"key": "value"},
            instance="123",
        )
        assert labeled_rle.dumps() == _DATA_LABELEDRLE
