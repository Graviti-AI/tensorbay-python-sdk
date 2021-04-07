#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
from quaternion import quaternion

from ...geometry import Transform3D, Vector3D
from .. import Box2DSubcatalog, Box3DSubcatalog, LabeledBox2D, LabeledBox3D
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@pytest.fixture
def subcatalog_contents(is_tracking_data, categories_catalog_data, attributes_catalog_data):
    return {
        "isTracking": is_tracking_data,
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
    }


class TestLabeledBox2D:
    def test_init(self):

        labeledbox2d = LabeledBox2D(
            1,
            2,
            4,
            6,
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox2d.category == "cat"
        assert labeledbox2d.attributes == {"gender": "male"}
        assert labeledbox2d.instance == 12345

        assert labeledbox2d[0] == 1
        assert labeledbox2d[1] == 2
        assert labeledbox2d[2] == 4
        assert labeledbox2d[3] == 6

    def test_eq(self):
        box2d1 = LabeledBox2D(1, 1, 3, 3, category="cat", attributes={"gender": "male"})
        box2d2 = LabeledBox2D(1, 1, 3, 3, category="cat", attributes={"gender": "male"})
        box2d3 = LabeledBox2D(1, 1, 4, 4, category="cat", attributes={"gender": "male"})

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
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox2d.category == "cat"
        assert labeledbox2d.attributes == {"gender": "male"}
        assert labeledbox2d.instance == 12345

        assert labeledbox2d[0] == xmin
        assert labeledbox2d[1] == xmax
        assert labeledbox2d[2] == ymin
        assert labeledbox2d[3] == ymax

    def test_loads(self):
        contents = {
            "box2d": {"xmin": 1, "ymin": 2, "xmax": 5, "ymax": 8},
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }
        labeledbox2d = LabeledBox2D.loads(contents)

        assert labeledbox2d.category == "cat"
        assert labeledbox2d.attributes == {"gender": "male"}
        assert labeledbox2d.instance == 12345

        assert labeledbox2d[0] == 1
        assert labeledbox2d[1] == 2
        assert labeledbox2d[2] == 5
        assert labeledbox2d[3] == 8

    def test_dumps(self):
        labeledbox2d = LabeledBox2D(
            1,
            2,
            5,
            8,
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox2d.dumps() == {
            "box2d": {"xmin": 1, "ymin": 2, "xmax": 5, "ymax": 8},
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }


class TestLabeledBox3D:
    def test_init(self):
        translation = Vector3D(1, 2, 3)
        rotation = quaternion(1, 2, 3, 4)
        size = Vector3D(1, 2, 3)

        labeledbox3d = LabeledBox3D(
            size=size,
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox3d.translation == translation
        assert labeledbox3d.rotation == rotation
        assert labeledbox3d.size == size
        assert labeledbox3d.category == "cat"
        assert labeledbox3d.attributes == {"gender": "male"}
        assert labeledbox3d.instance == 12345

    def test_rmul(self):
        size = [1, 2, 3]
        translation = [1, 2, 3]
        rotation = quaternion(0, 1, 0, 0)
        transform = Transform3D(translation, rotation)
        quaternion_1 = quaternion(1, 2, 3, 4)

        labeledbox3d = LabeledBox3D(
            size=size,
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox3d.__rmul__(transform) == LabeledBox3D(
            size=size,
            translation=[2, 0, 0],
            rotation=[-1, 0, 0, 0],
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox3d.__rmul__(quaternion_1) == LabeledBox3D(
            size=size,
            translation=[1.7999999999999996, 2, 2.6],
            rotation=[-2, 1, 4, -3],
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox3d.__rmul__(1) == NotImplemented

    def test_eq(self):
        translation = [1, 2, 3]
        rotation = quaternion(1, 2, 3, 4)

        box3d1 = LabeledBox3D(
            size=[1, 2, 3],
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
        )
        box3d2 = LabeledBox3D(
            size=[1, 2, 3],
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
        )
        box3d3 = LabeledBox3D(
            size=[1, 2, 5],
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
        )

        assert box3d1 == box3d2
        assert box3d1 != box3d3

    def test_loads(self):
        contents = {
            "box3d": {
                "translation": {"x": 1, "y": 2, "z": 3},
                "rotation": {"w": 1, "x": 2, "y": 3, "z": 4},
                "size": {"x": 1, "y": 2, "z": 3},
            },
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }
        labeledbox3d = LabeledBox3D.loads(contents)

        assert labeledbox3d.category == "cat"
        assert labeledbox3d.attributes == {"gender": "male"}
        assert labeledbox3d.instance == 12345

        assert labeledbox3d.translation == Vector3D(1, 2, 3)
        assert labeledbox3d.rotation == quaternion(1, 2, 3, 4)
        assert labeledbox3d.size == Vector3D(1, 2, 3)

    def test_dumps(self):
        translation = [1, 2, 3]
        rotation = quaternion(1, 2, 3, 4)
        size = [1, 2, 3]

        labeledbox3d = LabeledBox3D(
            size=size,
            translation=translation,
            rotation=rotation,
            category="cat",
            attributes={"gender": "male"},
            instance=12345,
        )

        assert labeledbox3d.dumps() == {
            "box3d": {
                "translation": {"x": 1, "y": 2, "z": 3},
                "rotation": {"w": 1, "x": 2, "y": 3, "z": 4},
                "size": {"x": 1, "y": 2, "z": 3},
            },
            "category": "cat",
            "attributes": {"gender": "male"},
            "instance": 12345,
        }


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
        subcatalog1 = SUBCATALOG.loads(contents1)
        subcatalog2 = SUBCATALOG.loads(contents1)
        subcatalog3 = SUBCATALOG.loads(contents2)

        assert subcatalog1 == subcatalog2
        assert subcatalog1 != subcatalog3

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_loads(self, SUBCATALOG, categories, attributes, subcatalog_contents):
        subcatalog = SUBCATALOG.loads(subcatalog_contents)

        assert subcatalog.is_tracking == subcatalog_contents["isTracking"]
        assert subcatalog.categories == categories
        assert subcatalog.attributes == attributes

    @pytest.mark.parametrize("SUBCATALOG", (Box2DSubcatalog, Box3DSubcatalog))
    def test_dumps(self, SUBCATALOG, categories, attributes, subcatalog_contents):
        subcatalog = SUBCATALOG()
        subcatalog.is_tracking = subcatalog_contents["isTracking"]
        subcatalog.categories = categories
        subcatalog.attributes = attributes

        # isTracking will not dumps out when isTracking is false
        if not subcatalog_contents["isTracking"]:
            del subcatalog_contents["isTracking"]
        assert subcatalog.dumps() == subcatalog_contents
