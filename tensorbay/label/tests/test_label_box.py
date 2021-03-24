#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
from quaternion import quaternion

from ...geometry import Transform3D, Vector3D
from .. import Box2DSubcatalog, Box3DSubcatalog, LabeledBox2D, LabeledBox3D
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "12345"

_LABELEDBOX2D_DATA = {
    "box2d": {"xmin": 1, "ymin": 2, "xmax": 5, "ymax": 8},
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}

_LABELEDBOX3D_DATA = {
    "box3d": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1, "x": 2, "y": 3, "z": 4},
        "size": {"x": 1, "y": 2, "z": 3},
    },
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}
_SUBCATALOG_CONTENT = {
    "isTracking": True,
    "categories": [{"name": "0"}, {"name": "1"}],
    "attributes": [{"name": "gender", "enum": ["male", "female"]}],
}


class TestLabeledBox2D:
    def test_init(self):
        xmin, xmax, ymin, ymax = 1, 2, 4, 6

        labeledbox2d = LabeledBox2D(
            xmin,
            ymin,
            xmax,
            ymax,
            category=_CATEGORY,
            attributes=_ATTRIBUTES,
            instance=_INSTANCE,
        )

        assert labeledbox2d.category == _CATEGORY
        assert labeledbox2d.attributes == _ATTRIBUTES
        assert labeledbox2d.instance == _INSTANCE

        assert labeledbox2d[0] == xmin
        assert labeledbox2d[1] == ymin
        assert labeledbox2d[2] == xmax
        assert labeledbox2d[3] == ymax

    def test_eq(self):
        box2d1 = LabeledBox2D(1, 1, 3, 3, category=_CATEGORY, attributes=_ATTRIBUTES)
        box2d2 = LabeledBox2D(1, 1, 3, 3, category=_CATEGORY, attributes=_ATTRIBUTES)
        box2d3 = LabeledBox2D(1, 1, 4, 4, category=_CATEGORY, attributes=_ATTRIBUTES)

        assert box2d1 == box2d2
        assert box2d1 != box2d3

    def test_from_xywh(self):
        x, y, width, height = 1, 2, 3, 4
        xmin, xmax, ymin, ymax = 1, 2, 4, 6

        labeledbox2d = LabeledBox2D.from_xywh(
            x,
            y,
            width,
            height,
            category=_CATEGORY,
            attributes=_ATTRIBUTES,
            instance=_INSTANCE,
        )

        assert labeledbox2d.category == _CATEGORY
        assert labeledbox2d.attributes == _ATTRIBUTES
        assert labeledbox2d.instance == _INSTANCE

        assert labeledbox2d[0] == xmin
        assert labeledbox2d[1] == xmax
        assert labeledbox2d[2] == ymin
        assert labeledbox2d[3] == ymax

    def test_loads(self):
        labeledbox2d = LabeledBox2D.loads(_LABELEDBOX2D_DATA)

        assert labeledbox2d.category == _LABELEDBOX2D_DATA["category"]
        assert labeledbox2d.attributes == _LABELEDBOX2D_DATA["attributes"]
        assert labeledbox2d.instance == _LABELEDBOX2D_DATA["instance"]

        assert labeledbox2d[0] == _LABELEDBOX2D_DATA["box2d"]["xmin"]
        assert labeledbox2d[1] == _LABELEDBOX2D_DATA["box2d"]["ymin"]
        assert labeledbox2d[2] == _LABELEDBOX2D_DATA["box2d"]["xmax"]
        assert labeledbox2d[3] == _LABELEDBOX2D_DATA["box2d"]["ymax"]

    def test_dumps(self):
        labeledbox2d = LabeledBox2D(
            1,
            2,
            5,
            8,
            category=_CATEGORY,
            attributes=_ATTRIBUTES,
            instance=_INSTANCE,
        )

        assert labeledbox2d.dumps() == _LABELEDBOX2D_DATA


class TestLabeledBox3D:
    def test_init(self):
        translation = Vector3D(1, 2, 3)
        rotation = quaternion(1, 2, 3, 4)
        size = Vector3D(1, 2, 3)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, size=size, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.translation == translation
        assert labeledbox3d.rotation == rotation
        assert labeledbox3d.size == size
        assert labeledbox3d.category == _CATEGORY
        assert labeledbox3d.attributes == _ATTRIBUTES
        assert labeledbox3d.instance == _INSTANCE

    def test_rmul(self):
        translation = [1, 2, 3]
        rotation = quaternion(0, 1, 0, 0)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.__rmul__(transform).category == _CATEGORY
        assert labeledbox3d.__rmul__(transform).attributes == _ATTRIBUTES
        assert labeledbox3d.__rmul__(transform).instance == _INSTANCE

        assert labeledbox3d.__rmul__(1) == NotImplemented

    def test_eq(self):
        translation = [1, 2, 3]
        rotation = quaternion(1, 2, 3, 4)
        transform = Transform3D(translation=translation, rotation=rotation)

        box3d1 = LabeledBox3D(transform, size=[1, 2, 3], category=_CATEGORY, attributes=_ATTRIBUTES)
        box3d2 = LabeledBox3D(transform, size=[1, 2, 3], category=_CATEGORY, attributes=_ATTRIBUTES)
        box3d3 = LabeledBox3D(transform, size=[1, 2, 5], category=_CATEGORY, attributes=_ATTRIBUTES)

        assert box3d1 == box3d2
        assert box3d1 != box3d3

    def test_loads(self):
        labeledbox3d = LabeledBox3D.loads(_LABELEDBOX3D_DATA)

        assert labeledbox3d.category == _LABELEDBOX3D_DATA["category"]
        assert labeledbox3d.attributes == _LABELEDBOX3D_DATA["attributes"]
        assert labeledbox3d.instance == _LABELEDBOX3D_DATA["instance"]

        assert labeledbox3d.translation == Vector3D(1, 2, 3)
        assert labeledbox3d.rotation == quaternion(1, 2, 3, 4)
        assert labeledbox3d.size == Vector3D(1, 2, 3)

    def test_dumps(self):
        translation = [1, 2, 3]
        rotation = quaternion(1, 2, 3, 4)
        size = [1, 2, 3]
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, size=size, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.dumps() == _LABELEDBOX3D_DATA


class TestBox2dAndBox3dSubcatalog:
    """This class used to test Box2DSubcatalog and Box3DSubcatalog classes."""

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_init_subclass(self, SUBCATALOG):
        subcatalog = SUBCATALOG()
        assert subcatalog._supports == (
            IsTrackingMixin,
            CategoriesMixin,
            AttributesMixin,
        )

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_eq(self, SUBCATALOG):
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
        subcatalog1 = SUBCATALOG.loads(content1)
        subcatalog2 = SUBCATALOG.loads(content1)
        subcatalog3 = SUBCATALOG.loads(content2)

        assert subcatalog1 == subcatalog2
        assert subcatalog1 != subcatalog3

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_loads(self, SUBCATALOG, categories, attributes):
        subcatalog = SUBCATALOG.loads(_SUBCATALOG_CONTENT)

        assert subcatalog.is_tracking == _SUBCATALOG_CONTENT["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_dumps(self, SUBCATALOG, categories, attributes):
        subcatalog = SUBCATALOG()
        subcatalog.is_tracking = _SUBCATALOG_CONTENT["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes
        assert subcatalog.dumps() == _SUBCATALOG_CONTENT
