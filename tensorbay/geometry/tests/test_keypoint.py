#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Box2D, Keypoint2D, Keypoints2D, Vector2D

_DATA_KEYPOINT = {"x": 1.0, "y": 1.0, "v": 1}
_DATA_KEYPOINTS = [{"x": 1.0, "y": 1.0, "v": 1}, {"x": 2.0, "y": 2.0, "v": 2}]


class TestKeypoint2D:
    def test_init(self):
        assert Keypoint2D(*[1, 1, 1]) == Keypoint2D(1, 1, 1)
        assert Keypoint2D(x=1, y=1, v=1) == Keypoint2D(1, 1, 1)

        keypoint = Keypoint2D(1, 1, 1)
        assert keypoint.v == 1

    def test_neg(self):
        keypoint = Keypoint2D(1, 1, 1)
        assert -keypoint == Vector2D(-1, -1)

    def test_loads(self):
        keypoint = Keypoint2D.loads(_DATA_KEYPOINT)
        assert keypoint._data == (1, 1, 1)

    def test_dumps(self):
        keypoint = Keypoint2D(1, 1, 1)
        assert keypoint.dumps() == _DATA_KEYPOINT


class TestKeypoints2D:
    def test_init(self):
        sequence = [[1, 2], [2, 3]]
        assert Keypoints2D(None) == Keypoints2D([])
        assert Keypoints2D(sequence) == Keypoints2D([Keypoint2D(1, 2), Keypoint2D(2, 3)])

    def test_eq(self):
        keypoints_1 = Keypoints2D([[1, 2], [2, 3]])
        keypoints_2 = Keypoints2D([[1, 2], [2, 3]])
        keypoints_3 = Keypoints2D([[1, 2], [3, 3]])
        assert (keypoints_1 == keypoints_2) == True
        assert (keypoints_1 == keypoints_3) == False

    def test_loads(self):
        keypoints = Keypoints2D.loads(_DATA_KEYPOINTS)
        assert keypoints._data == [Keypoint2D(1.0, 1.0, 1), Keypoint2D(2.0, 2.0, 2)]

    def test_dumps(self):
        keypoints = Keypoints2D([[1, 1, 1], [2, 2, 2]])
        assert keypoints.dumps() == _DATA_KEYPOINTS

    def test_bounds(self):
        keypoints = Keypoints2D([[1, 2], [2, 3]])
        assert keypoints.bounds() == Box2D(1, 2, 2, 3)
