#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from ...geometry import Polygon2D, Vector2D
from .. import LabeledPolygon2D

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "12345"

_LABELEDPOLYGON2D_DATA = {
    "polygon2d": [
        {"x": 1, "y": 2},
    ],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}


class TestLabeledPolygon2D:
    def test_init(self):
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygon2d[0] == Vector2D(1, 2)
        assert labeledpolygon2d.category == _CATEGORY
        assert labeledpolygon2d.attributes == _ATTRIBUTES
        assert labeledpolygon2d.instance == _INSTANCE

    def test_loads(self):
        labeledpolygon2d = LabeledPolygon2D.loads(_LABELEDPOLYGON2D_DATA)

        assert labeledpolygon2d[0] == Vector2D(1, 2)
        assert labeledpolygon2d.category == _LABELEDPOLYGON2D_DATA["category"]
        assert labeledpolygon2d.attributes == _LABELEDPOLYGON2D_DATA["attributes"]
        assert labeledpolygon2d.instance == _LABELEDPOLYGON2D_DATA["instance"]

    def test_dumps(self):
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygon2d.dumps() == _LABELEDPOLYGON2D_DATA
