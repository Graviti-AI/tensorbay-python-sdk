#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
from quaternion import quaternion

from .. import Box2D, Box3D, Transform3D, Vector2D, Vector3D

_DATA_2D = {"xmin": 1.0, "ymin": 2.0, "xmax": 3.0, "ymax": 4.0}
_DATA_3D = {
    "size": {"x": 1.0, "y": 2.0, "z": 3.0},
    "translation": {"x": 1.0, "y": 2.0, "z": 3.0},
    "rotation": {"w": 0.0, "x": 1.0, "y": 0.0, "z": 0.0},
}


class TestBox2D:
    def test_init(self):
        with pytest.raises(TypeError):
            Box2D()
        with pytest.raises(TypeError):
            Box2D(1)
        with pytest.raises(TypeError):
            Box2D(x=0)
        with pytest.raises(TypeError):
            Box2D()
        with pytest.raises(TypeError):
            Box2D([1, 2, 3, 4])

        assert Box2D(*[1, 2, 3, 4]) == Box2D(1, 2, 3, 4)

        box2d = Box2D(1, 2, 3, 4)
        assert box2d.xmin == 1
        assert box2d.ymin == 2
        assert box2d.xmax == 3
        assert box2d.ymax == 4
        assert box2d.tl == Vector2D(1, 2)
        assert box2d.br == Vector2D(3, 4)
        assert box2d.width == 2
        assert box2d.height == 2

    def test_len(self):
        box2d = Box2D(1, 2, 3, 4)
        assert len(box2d) == 4

    def test_eq(self):
        box2d_1 = Box2D(1, 2, 3, 4)
        box2d_2 = Box2D(1, 2, 3, 4)
        assert (box2d_1 == box2d_2) == True

        box2d_3 = Box2D(2, 3, 4, 5)
        assert (box2d_1 == box2d_3) == False

    def test_and(self):
        box2d_1 = Box2D(1, 2, 3, 4)
        box2d_2 = Box2D(2, 3, 4, 5)
        assert (box2d_1 & box2d_2) == Box2D(2, 3, 3, 4)

    def test_repr_head(self):
        box2d = Box2D(1, 2, 3, 4)
        assert box2d._repr_head() == "Box2D(1, 2, 3, 4)"

    def test_iou(self):
        box2d_1 = Box2D(1, 2, 3, 4)
        box2d_2 = Box2D(2, 2, 3, 4)
        assert Box2D.iou(box2d_1, box2d_2) == 0.5

    def test_from_xywh(self):
        assert Box2D.from_xywh(x=1, y=2, width=3, height=4) == Box2D(1, 2, 4, 6)
        assert Box2D.from_xywh(x=1, y=2, width=-1, height=2) == Box2D(0, 0, 0, 0)

    def test_loads(self):
        box2d = Box2D.loads(_DATA_2D)
        assert box2d._data == (1, 2, 3, 4)

    def test_dumps(self):
        box2d = Box2D(1, 2, 3, 4)
        assert box2d.dumps() == _DATA_2D

    def test_area(self):
        box2d = Box2D(1, 2, 3, 4)
        assert box2d.area() == 4


class TestBox3D:
    def test_init(self):
        translation = Vector3D(1, 2, 3)
        rotation = quaternion(0, 1, 0, 0)
        size = Vector3D(1, 2, 3)
        transform = Transform3D(translation=translation, rotation=rotation)

        box3d = Box3D(transform)
        assert box3d.translation == translation
        assert box3d.rotation == rotation

        box3d = Box3D(translation=translation, rotation=rotation, size=size)
        assert box3d.translation == translation
        assert box3d.rotation == rotation
        assert box3d.size == size

    def test_eq(self):
        box3d_1 = Box3D()
        box3d_2 = Box3D()
        box3d_3 = Box3D(translation=[1, 2, 3])
        assert (box3d_1 == box3d_2) == True
        assert (box3d_1 == box3d_3) == False

    def test_rmul(self):
        transform = Transform3D(translation=[1, 2, 3], rotation=quaternion(0, 1, 0, 0))
        box3d = Box3D(transform)
        assert box3d.__rmul__(transform) == Box3D(
            translation=[2, 0, 0], rotation=quaternion(-1, 0, 0, 0)
        )
        assert box3d.__rmul__(1) == NotImplemented

    def test_line_intersect(self):
        assert Box3D._line_intersect(4, 4, 1) == 3.0

    def test_loads(self):
        box3d = Box3D.loads(_DATA_3D)
        assert box3d.translation == Vector3D(1, 2, 3)
        assert box3d.rotation == quaternion(0, 1, 0, 0)
        assert box3d.size == Vector3D(1, 2, 3)

    def test_dumps(self):

        box3d = Box3D(
            translation=Vector3D(1, 2, 3),
            rotation=quaternion(0, 1, 0, 0),
            size=Vector3D(1, 2, 3),
        )
        assert box3d.dumps() == _DATA_3D

    def test_iou(self):
        box3d_1 = Box3D(size=[1, 1, 1])
        box3d_2 = Box3D(size=[2, 2, 2])
        assert Box3D.iou(box3d_1, box3d_2) == 0.125
