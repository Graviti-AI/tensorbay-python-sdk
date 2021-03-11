#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.  #

from ...geometry import Vector2D
from .. import LabeledPolyline2D, Polyline2DSubcatalog
from ..supports import SupportAttributes, SupportCategories, SupportIsTracking

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "12345"


_LABELEDPOLYLINE2D_DATA = {
    "polyline2d": [{"x": 1, "y": 2}],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}
_POLYLINE_SUBCATALOG = {
    "isTracking": True,
    "categories": [{"name": "0"}, {"name": "1"}],
    "attributes": [{"name": "gender", "enum": ["male", "female"]}],
}


class TestLabeledPolyline2D:
    def test_init(self):
        labeledpolyline2d = LabeledPolyline2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolyline2d[0] == Vector2D(1, 2)
        assert labeledpolyline2d.category == _CATEGORY
        assert labeledpolyline2d.attributes == _ATTRIBUTES
        assert labeledpolyline2d.instance == _INSTANCE

    def test_eq(self):
        polyline1 = LabeledPolyline2D([[1, 1], [1, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)
        polyline2 = LabeledPolyline2D([[1, 1], [1, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)
        polyline3 = LabeledPolyline2D([[1, 1], [2, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)

        assert polyline1 == polyline2
        assert polyline1 != polyline3

    def test_loads(self):
        labeledpolygonline2d = LabeledPolyline2D.loads(_LABELEDPOLYLINE2D_DATA)

        assert labeledpolygonline2d[0] == Vector2D(1, 2)
        assert labeledpolygonline2d.category == _LABELEDPOLYLINE2D_DATA["category"]
        assert labeledpolygonline2d.attributes == _LABELEDPOLYLINE2D_DATA["attributes"]
        assert labeledpolygonline2d.instance == _LABELEDPOLYLINE2D_DATA["instance"]

    def test_dumps(self):
        labeledpolygonline2d = LabeledPolyline2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygonline2d.dumps() == _LABELEDPOLYLINE2D_DATA


class TestKeypoints2DSubcatalog:
    def test_init_subclass(self):
        subcatalog = Polyline2DSubcatalog()
        assert subcatalog._supports == (
            SupportIsTracking,
            SupportCategories,
            SupportAttributes,
        )

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
        polyline2d_subcatalog1 = Polyline2DSubcatalog.loads(content1)
        polyline2d_subcatalog2 = Polyline2DSubcatalog.loads(content1)
        polyline2d_subcatalog3 = Polyline2DSubcatalog.loads(content2)

        assert polyline2d_subcatalog1 == polyline2d_subcatalog2
        assert polyline2d_subcatalog1 != polyline2d_subcatalog3

    def test_loads(self, categories, attributes):
        subcatalog = Polyline2DSubcatalog.loads(_POLYLINE_SUBCATALOG)

        assert subcatalog.is_tracking == _POLYLINE_SUBCATALOG["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes):
        subcatalog = Polyline2DSubcatalog()
        subcatalog.is_tracking = _POLYLINE_SUBCATALOG["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes
        assert subcatalog.dumps() == _POLYLINE_SUBCATALOG
