#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Vector, Vector2D, Vector3D

_DATA = [{"x": 1.0, "y": 2.0}, {"x": 1.0, "y": 2.0, "z": 3.0}]


class TestVector:
    def test_new_class(self):
        with pytest.raises(TypeError):
            Vector([1, 2])
        with pytest.raises(TypeError):
            Vector(1)
        with pytest.raises(TypeError):
            Vector(1, 2, 3, 4)
        assert Vector(1, 2) == Vector2D(1, 2)
        assert Vector(1, 2, 3) == Vector3D(1, 2, 3)
        assert Vector(*[1, 2]) == Vector2D(1, 2)

    def test_bool(self):
        vector = Vector(0, 0)
        assert bool(vector) == False

        vector = Vector(1, 1)
        assert bool(vector) == True

    def test_neg(self):
        vector = Vector(1, 1)
        assert -vector == Vector2D(-1, -1)

    def test_eq(self):
        vector_1 = Vector(1, 2)
        vector_2 = Vector(1, 2)
        vector_3 = Vector(1, 3)
        vector_4 = Vector(1, 2, 3)
        assert (vector_1 == vector_2) == True
        assert (vector_1 == vector_3) == False
        assert (vector_1 == vector_4) == False
        assert (vector_1 == (1, 2)) == False

    def test_add(self):
        vector_2d = Vector(1, 2)
        vector_3d = Vector(1, 2, 3)
        with pytest.raises(TypeError):
            vector_2d + vector_3d
        with pytest.raises(TypeError):
            vector_2d + (1, 2, 3)
        with pytest.raises(TypeError):
            vector_2d + 1
        assert Vector(1, 1) + Vector(1, 1) == Vector(2, 2)
        assert Vector(1, 1) + (1, 1) == Vector(2, 2)
        assert Vector(1, 1, 1) + Vector(1, 1, 1) == Vector(2, 2, 2)
        assert Vector(1, 1, 1) + (1, 1, 1) == Vector(2, 2, 2)

    def test_radd(self):
        vector = Vector(1, 2)
        assert [1, 1] + vector == Vector(2, 3)

    def test_repr_head(self):
        vector = Vector(1, 2)
        assert vector._repr_head() == "Vector2D(1, 2)"

    def test_loads(self):
        vector = Vector.loads(_DATA[0])
        assert vector._data == (1, 2)

        vector = Vector.loads(_DATA[1])
        assert vector._data == (1, 2, 3)

    def test_dumps(self):
        vector = Vector(1, 2)
        assert vector.dumps() == _DATA[0]

        vector = Vector(1, 2, 3)
        assert vector.dumps() == _DATA[1]


class TestVector2D:
    def test_init(self):
        with pytest.raises(TypeError):
            Vector2D(1, 2, 3)
        with pytest.raises(TypeError):
            Vector2D([1, 2])
        with pytest.raises(TypeError):
            Vector2D()

        assert Vector2D(*[1, 2]) == Vector2D(1, 2)
        assert Vector2D(x=1, y=1) == Vector2D(1, 1)

        vector_2d = Vector2D(1, 2)
        assert vector_2d.x == 1
        assert vector_2d.y == 2

    def test_loads(self):
        vector = Vector2D.loads(_DATA[0])
        assert vector._data == (1, 2)

    def test_dumps(self):
        vector = Vector2D(1, 2)
        assert vector.dumps() == _DATA[0]


class TestVector3D:
    def test_init(self):
        with pytest.raises(TypeError):
            Vector3D(1, 2)
        with pytest.raises(TypeError):
            Vector3D([1, 2, 3])
        with pytest.raises(TypeError):
            Vector3D()

        assert Vector3D(*[1, 2, 3]) == Vector3D(1, 2, 3)
        assert Vector3D(x=1, y=2, z=3) == Vector3D(1, 2, 3)

        vector_3d = Vector3D(1, 2, 3)
        assert vector_3d.x == 1
        assert vector_3d.y == 2
        assert vector_3d.z == 3

    def test_loads(self):
        vector = Vector3D.loads(_DATA[1])
        assert vector._data == (1, 2, 3)

    def test_dumps(self):
        vector = Vector3D(1, 2, 3)
        assert vector.dumps() == _DATA[1]
