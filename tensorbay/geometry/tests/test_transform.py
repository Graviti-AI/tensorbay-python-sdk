#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import numpy as np
import pytest
from quaternion import quaternion

from .. import Transform3D, Vector3D

_DATA_TRANSFORM = {
    "translation": {"x": 1.0, "y": 2.0, "z": 3.0},
    "rotation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
}


class TestTransform3D:
    def test_init(self):
        sequence = [[1, 0, 0, 1], [0, 1, 0, 1]]
        with pytest.raises(ValueError):
            Transform3D(sequence)

        transform = Transform3D(None)
        assert transform.translation == Vector3D(0.0, 0.0, 0.0)
        assert transform.rotation == quaternion(1.0, 0.0, 0.0, 0.0)

        sequence = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]
        transform = Transform3D(sequence)
        assert transform.translation == Vector3D(1, 1, 1)
        assert transform.rotation == quaternion(1.0, -0.0, -0.0, -0.0)

        numpy = np.array(sequence)
        transform = Transform3D(numpy)
        assert transform.translation == Vector3D(1, 1, 1)
        assert transform.rotation == quaternion(1.0, -0.0, -0.0, -0.0)

        transform_1 = Transform3D(transform)
        assert transform_1.translation == Vector3D(1, 1, 1)
        assert transform_1.rotation == quaternion(1.0, -0.0, -0.0, -0.0)

        transform = Transform3D(translation=[1, 2, 3], rotation=[1, 0, 0, 0])
        assert transform.translation == Vector3D(1, 2, 3)
        assert transform.rotation == quaternion(1.0, 0.0, 0.0, 0.0)

    def test_eq(self):
        transform_1 = Transform3D(translation=[1, 2, 3], rotation=[1, 0, 0, 0])
        transform_2 = Transform3D(translation=[1, 2, 3], rotation=[1, 0, 0, 0])
        transform_3 = Transform3D(translation=[1, 1, 1], rotation=[1, 0, 0, 0])
        assert (transform_1 == transform_2) == True
        assert (transform_1 == transform_3) == False

    def test_mul(self):
        sequence = [1, 1, 1]
        quaternion_1 = quaternion(0, 1, 0, 0)
        transform_1 = Transform3D(translation=[1, 2, 3], rotation=[0, 1, 0, 0])
        transform_2 = Transform3D(translation=[2, 0, 0], rotation=[-1, 0, 0, 0])
        transform_3 = Transform3D(translation=[1, 2, 3], rotation=[-1, 0, 0, 0])

        with pytest.raises(TypeError):
            transform_1 * 1
        assert transform_1 * transform_1 == transform_2
        assert transform_1 * quaternion_1 == transform_3
        assert transform_1 * sequence == Vector3D(2.0, 1.0, 2.0)

    def test_rmul(self):
        quaternion_1 = quaternion(0, 1, 0, 0)
        transform_1 = Transform3D(translation=[1, 2, 3], rotation=[0, 1, 0, 0])
        transform_2 = Transform3D(translation=[1, -2, -3], rotation=[-1, 0, 0, 0])

        with pytest.raises(TypeError):
            1 * transform_1
        assert quaternion_1 * transform_1 == transform_2

    def test_create(self):
        transform = Transform3D(translation=[1, 2, 3], rotation=[0, 1, 0, 0])
        assert Transform3D._create(Vector3D(1, 2, 3), quaternion(0, 1, 0, 0)) == transform

    def test_loads(self):
        transform = Transform3D.loads(_DATA_TRANSFORM)
        assert transform.translation == Vector3D(1.0, 2.0, 3.0)
        assert transform.rotation == quaternion(1.0, 0.0, 0.0, 0.0)

    def test_dumps(self):
        transform = Transform3D(translation=[1, 2, 3], rotation=[1, 0, 0, 0])
        assert transform.dumps() == _DATA_TRANSFORM

    def test_set_translation(self):
        transform = Transform3D()

        transform.set_translation(1, 2, 3)
        assert transform.translation == Vector3D(1, 2, 3)
        transform.set_translation(x=3, y=4, z=5)
        assert transform.translation == Vector3D(3, 4, 5)

    def test_set_rotation(self):
        transform = Transform3D()

        transform.set_rotation([0, 1, 0, 0])
        assert transform.rotation == quaternion(0, 1, 0, 0)

        quaternion_1 = quaternion(0, 1, 0, 0)
        transform.set_rotation(quaternion_1)
        assert transform.rotation == quaternion_1

    def test_as_matrix(self):
        matrix = np.array([[1, 0, 0, 1], [0, -1, 0, 2], [0, 0, -1, 3], [0, 0, 0, 1]])
        transform = Transform3D(translation=[1, 2, 3], rotation=[0, 1, 0, 0])
        np.testing.assert_array_equal(transform.as_matrix(), matrix)

    def test_inverse(self):
        transform_1 = Transform3D(translation=[1, 2, 3], rotation=[0, 1, 0, 0])
        transform_2 = Transform3D(translation=[-1, 2, 3], rotation=[0, -1, 0, 0])
        assert transform_1.inverse() == transform_2
