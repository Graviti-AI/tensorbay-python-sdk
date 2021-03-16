#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import warnings

import numpy as np
import pytest

from .. import Quaternion, Vector3D

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import quaternion

_DATA = {"w": 1, "x": 0, "y": 0, "z": 0}


class TestQuaternion:
    def test_init(self):
        with pytest.raises(TypeError):
            Quaternion([[1]])

        assert Quaternion(1) == Quaternion(1.0, 0.0, 0.0, 0.0)
        assert Quaternion(w=1, x=0, y=0, z=0) == Quaternion(1.0, 0.0, 0.0, 0.0)
        assert Quaternion([1.0, 0.0, 0.0, 0.0]) == Quaternion(1.0, 0.0, 0.0, 0.0)
        assert Quaternion([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == Quaternion(1.0, 0.0, 0.0, 0.0)
        assert Quaternion(None) == Quaternion(1.0, 0.0, 0.0, 0.0)
        assert Quaternion(rotation_vector=[0, 0, 0]) == Quaternion(1.0, 0.0, 0.0, 0.0)

        quaternion_1 = Quaternion(0.7073882691671998, 0.706825181105366, 0.0, 0.0)
        assert Quaternion(axis=[1, 0, 0], radians=1.57) == quaternion_1
        assert quaternion_1.w == 0.7073882691671998
        assert quaternion_1.x == 0.706825181105366
        assert quaternion_1.y == 0.0
        assert quaternion_1.z == 0.0
        assert quaternion_1.radians == 1.5700000000000003

        quaternion_1 = Quaternion(0.7071067811865476, 0.7071067811865475, 0.0, 0.0)
        assert quaternion.allclose(Quaternion(axis=[1, 0, 0], degrees=90)._data, quaternion_1._data)
        assert quaternion_1.degrees == 89.99999999999999

        quaternion_1 = Quaternion(0.7073882691671998, -0.0, 0.706825181105366, 0.0)
        assert Quaternion(spherical_coords=[1.57, 0.0]) == quaternion_1
        assert Quaternion(euler_angle=[0, 1.57, 0]) == quaternion_1

    def test_repr(self):
        quaternion_1 = Quaternion()
        assert quaternion_1.__repr__() == "Quaternion(1.0, 0.0, 0.0, 0.0)"

    def test_bool(self):
        quaternion_1 = Quaternion(0, 0, 0, 0)
        assert bool(quaternion_1) == False

        quaternion_1 = Quaternion()
        assert bool(quaternion_1) == True

    def test_neg(self):
        quaternion_1 = Quaternion()
        assert -quaternion_1 == Quaternion(-1.0, -0.0, -0.0, -0.0)

    def test_eq(self):
        quaternion_1 = Quaternion()
        quaternion_2 = Quaternion()
        assert (quaternion_1 == quaternion_2) == True

        quaternion_2 = Quaternion(0, 1, 0, 0)
        assert (quaternion_1 == quaternion_2) == False
        assert (quaternion_1 == 0) == False

    def test_add(self):
        quaternion_1 = Quaternion()
        quaternion_2 = Quaternion()
        assert quaternion_1 + quaternion_2 == Quaternion(2.0, 0.0, 0.0, 0.0)
        assert quaternion_1.__add__(0) == NotImplemented

    def test_sub(self):
        quaternion_1 = Quaternion()
        quaternion_2 = Quaternion()
        assert quaternion_1 - quaternion_2 == Quaternion(0.0, 0.0, 0.0, 0.0)
        assert quaternion_1.__sub__(0) == NotImplemented

    def test_mul(self):
        quaternion_1 = Quaternion(1, 2, 3, 4)
        quaternion_2 = Quaternion()
        assert quaternion_1 * quaternion_2 == Quaternion(1.0, 2.0, 3.0, 4.0)
        assert quaternion_1 * 2 == Quaternion(2.0, 4.0, 6.0, 8.0)
        assert quaternion_1 * [1, 2] == [
            Quaternion(1.0, 2.0, 3.0, 4.0),
            Quaternion(2.0, 4.0, 6.0, 8.0),
        ]
        assert quaternion_1 * Vector3D(1, 2, 3) == Vector3D(
            Quaternion(1.0, 2.0, 3.0, 4.0),
            Quaternion(2.0, 4.0, 6.0, 8.0),
            Quaternion(3.0, 6.0, 9.0, 12.0),
        )
        np.testing.assert_equal(
            quaternion_1 * np.array([[1, 2], [3, 4]]),
            np.array(
                [
                    [Quaternion(1.0, 2.0, 3.0, 4.0), Quaternion(2.0, 4.0, 6.0, 8.0)],
                    [Quaternion(3.0, 6.0, 9.0, 12.0), Quaternion(4.0, 8.0, 12.0, 16.0)],
                ]
            ),
        )

    def test_rmul(self):
        quaternion_1 = Quaternion(1, 2, 3, 4)
        assert 2 * quaternion_1 == Quaternion(2.0, 4.0, 6.0, 8.0)
        assert [1, 2] * quaternion_1 == [
            Quaternion(1.0, 2.0, 3.0, 4.0),
            Quaternion(2.0, 4.0, 6.0, 8.0),
        ]
        assert Vector3D(1, 2, 3) * quaternion_1 == Vector3D(
            Quaternion(1.0, 2.0, 3.0, 4.0),
            Quaternion(2.0, 4.0, 6.0, 8.0),
            Quaternion(3.0, 6.0, 9.0, 12.0),
        )
        np.testing.assert_equal(
            np.array([[1, 2], [3, 4]]) * quaternion_1,
            np.array(
                [
                    [Quaternion(1.0, 2.0, 3.0, 4.0), Quaternion(2.0, 4.0, 6.0, 8.0)],
                    [Quaternion(3.0, 6.0, 9.0, 12.0), Quaternion(4.0, 8.0, 12.0, 16.0)],
                ]
            ),
        )

    def test_create(self):
        assert Quaternion._create(quaternion.quaternion(1, 0, 0, 0)) == Quaternion(1, 0, 0, 0)

    def test_loads(self):
        quaternion_1 = Quaternion.loads(_DATA)
        assert quaternion.allclose(quaternion_1._data, quaternion.quaternion(1, 0, 0, 0))

    def test_dumps(self):
        quaternion_1 = Quaternion(1.0, 0.0, 0.0, 0.0)
        assert quaternion_1.dumps() == _DATA

    def test_as_matrix(self):
        quaternion_1 = Quaternion()
        np.testing.assert_array_equal(
            quaternion_1.as_matrix(), np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        )

    def test_inverse(self):
        quaternion_1 = Quaternion()
        assert quaternion_1.inverse() == Quaternion(1.0, -0.0, -0.0, -0.0)

    def test_rotate(self):
        quaternion_1 = Quaternion()

        with pytest.raises(ValueError):
            quaternion_1.rotate([1, 2])
        with pytest.raises(ValueError):
            quaternion_1.rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        assert quaternion_1.rotate([1, 2, 3]) == Vector3D(1.0, 2.0, 3.0)
        assert quaternion_1.rotate(np.array([1, 2, 3])) == Vector3D(1.0, 2.0, 3.0)
