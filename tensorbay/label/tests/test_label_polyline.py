#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.  #

import pytest

from ...geometry import Vector2D
from .. import LabeledPolyline2D, Polyline2DSubcatalog
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin

_LABELEDPOLYLINE2D_DATA = {
    "polyline2d": [{"x": 1, "y": 2}],
    "category": "cat",
    "attributes": {"gender": "male"},
    "instance": "12345",
}


@pytest.fixture
def subcatalog_polyline(is_tracking_data, categories_catalog_data, attributes_catalog_data):
    return {
        "isTracking": is_tracking_data,
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
    }


class TestLabeledPolyline2D:
    def test_init(self):
        labeledpolyline2d = LabeledPolyline2D(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolyline2d[0] == Vector2D(1, 2)
        assert labeledpolyline2d.category == "cat"
        assert labeledpolyline2d.attributes == {"gender": "male"}
        assert labeledpolyline2d.instance == "12345"

    def test_eq(self):
        polyline1 = LabeledPolyline2D(
            [[1, 1], [1, 2]], category="cat", attributes={"gender": "male"}
        )
        polyline2 = LabeledPolyline2D(
            [[1, 1], [1, 2]], category="cat", attributes={"gender": "male"}
        )
        polyline3 = LabeledPolyline2D(
            [[1, 1], [2, 2]], category="cat", attributes={"gender": "male"}
        )

        assert polyline1 == polyline2
        assert polyline1 != polyline3

    def test_loads(self):
        contents = {
            "polyline2d": [{"x": 1, "y": 2}],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": "12345",
        }
        labeledpolygonline2d = LabeledPolyline2D.loads(contents)

        assert labeledpolygonline2d[0] == Vector2D(1, 2)
        assert labeledpolygonline2d.category == "cat"
        assert labeledpolygonline2d.attributes == {"gender": "male"}
        assert labeledpolygonline2d.instance == "12345"

    def test_dumps(self):
        labeledpolygonline2d = LabeledPolyline2D(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolygonline2d.dumps() == {
            "polyline2d": [{"x": 1, "y": 2}],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": "12345",
        }


class TestPolyline2DSubcatalog:
    def test_init(self, is_tracking_data):
        polyline2d_subcatalog = Polyline2DSubcatalog
        polyline2d_subcatalog.is_tracking = is_tracking_data

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
        polyline2d_subcatalog1 = Polyline2DSubcatalog.loads(contents1)
        polyline2d_subcatalog2 = Polyline2DSubcatalog.loads(contents1)
        polyline2d_subcatalog3 = Polyline2DSubcatalog.loads(contents2)

        assert polyline2d_subcatalog1 == polyline2d_subcatalog2
        assert polyline2d_subcatalog1 != polyline2d_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_polyline):
        subcatalog = Polyline2DSubcatalog.loads(subcatalog_polyline)

        assert subcatalog.is_tracking == subcatalog_polyline["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes, subcatalog_polyline):
        subcatalog = Polyline2DSubcatalog()
        subcatalog.is_tracking = subcatalog_polyline["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes

        # isTracking will not dumps out when isTracking is false
        if not subcatalog_polyline["isTracking"]:
            del subcatalog_polyline["isTracking"]

        assert subcatalog.dumps() == subcatalog_polyline
