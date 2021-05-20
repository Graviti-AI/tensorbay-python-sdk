#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import Vector2D
from .. import LabeledPolygon2D, Polygon2DSubcatalog
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@pytest.fixture
def subcatalog_polygon(is_tracking_data, categories_catalog_data, attributes_catalog_data):
    return {
        "isTracking": is_tracking_data,
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
    }


class TestLabeledPolygon2D:
    def test_init(self):
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolygon2d[0] == Vector2D(1, 2)
        assert labeledpolygon2d.category == "cat"
        assert labeledpolygon2d.attributes == {"gender": "male"}
        assert labeledpolygon2d.instance == "12345"

    def test_eq(self):
        polygon1 = LabeledPolygon2D([[1, 1], [1, 2]], category="cat", attributes={"gender": "male"})
        polygon2 = LabeledPolygon2D([[1, 1], [1, 2]], category="cat", attributes={"gender": "male"})
        polygon3 = LabeledPolygon2D([[1, 1], [1, 3]], category="cat", attributes={"gender": "male"})

        assert polygon1 == polygon2
        assert polygon1 != polygon3

    def test_loads(self):
        content = {
            "polygon2d": [
                {"x": 1, "y": 2},
            ],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }
        labeledpolygon2d = LabeledPolygon2D.loads(content)

        assert labeledpolygon2d[0] == Vector2D(1, 2)
        assert labeledpolygon2d.category == "cat"
        assert labeledpolygon2d.attributes == {"gender": "male"}
        assert labeledpolygon2d.instance == 12345

    def test_dumps(self):
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category="cat", attributes={"gender": "male"}, instance="12345"
        )

        assert labeledpolygon2d.dumps() == {
            "polygon2d": [
                {"x": 1, "y": 2},
            ],
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": "12345",
        }


class TestPolygon2DSubcatalog:
    def test_init(self, is_tracking_data):
        polygon2d_subcatalog = Polygon2DSubcatalog(is_tracking_data)
        polygon2d_subcatalog.is_tracking = is_tracking_data

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
        polygon2d_subcatalog1 = Polygon2DSubcatalog.loads(content1)
        polygon2d_subcatalog2 = Polygon2DSubcatalog.loads(content1)
        polygon2d_subcatalog3 = Polygon2DSubcatalog.loads(content2)

        assert polygon2d_subcatalog1 == polygon2d_subcatalog2
        assert polygon2d_subcatalog1 != polygon2d_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_polygon):
        subcatalog = Polygon2DSubcatalog.loads(subcatalog_polygon)

        assert subcatalog.is_tracking == subcatalog_polygon["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes, subcatalog_polygon):
        subcatalog = Polygon2DSubcatalog()
        subcatalog.is_tracking = subcatalog_polygon["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes

        # isTracking will not dumps out when isTracking is false
        if not subcatalog_polygon["isTracking"]:
            del subcatalog_polygon["isTracking"]

        assert subcatalog.dumps() == subcatalog_polygon
