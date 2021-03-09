#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from itertools import zip_longest

import numpy as np
import pytest

from .. import Box2D, Polyline2D, Vector2D

_POLYLINE_INFO_1 = [
    {
        "vector": np.array([0, 1], dtype=np.float32),
        "last_time": 0,
        "time": 0.5,
        "point": np.array([1, 1], dtype=np.float32),
        "index": 0,
    },
    {
        "vector": np.array([1, 0], dtype=np.float32),
        "last_time": 0.5,
        "time": 1.0,
        "point": np.array([1, 2], dtype=np.float32),
        "index": 1,
    },
]
_POLYLINE_INFO_2 = [
    {
        "vector": np.array([-9, 12], dtype=np.float32),
        "last_time": 0,
        "time": 0.75,
        "point": np.array([10, -9], dtype=np.float32),
        "index": 0,
    },
    {
        "vector": np.array([3, 4], dtype=np.float32),
        "last_time": 0.75,
        "time": 1.0,
        "point": np.array([1, 3], dtype=np.float32),
        "index": 1,
    },
]
_POLYLINE_DATA = [{"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 2}]


class TestPolyline2D:
    def test_init(self):
        sequence = [[1, 1], [1, 2], [2, 2]]
        assert Polyline2D() == Polyline2D([])
        assert Polyline2D(sequence) == Polyline2D([Vector2D(1, 1), Vector2D(1, 2), Vector2D(2, 2)])

    def test_eq(self):
        polyline_1 = Polyline2D([[1, 2], [2, 3], [2, 2]])
        polyline_2 = Polyline2D([[1, 2], [2, 3], [2, 2]])
        polyline_3 = Polyline2D([[1, 2], [3, 4], [2, 2]])
        assert (polyline_1 == polyline_2) == True
        assert (polyline_1 == polyline_3) == False

    def test_distance(self):
        sequence_1 = [1, 2]
        sequence_2 = [4, 6]
        assert Polyline2D._distance(sequence_1, sequence_2) == 5.0

    def test_get_polyline_info(self):
        sequence = [[1, 1], [1, 2], [2, 2]]
        polyline_info = Polyline2D._get_polyline_info(sequence)

        for info1, info2 in zip_longest(polyline_info, _POLYLINE_INFO_1):
            assert info1["last_time"] == info2["last_time"]
            assert info1["time"] == info2["time"]
            assert info1["index"] == info2["index"]
            np.testing.assert_array_equal(info1["vector"], info2["vector"])
            np.testing.assert_array_equal(info1["point"], info2["point"])

    def test_insert_point(self):
        inserted_point = Polyline2D._insert_point(_POLYLINE_INFO_1[0], _POLYLINE_INFO_2[0])
        assert inserted_point["index"] == 1
        np.testing.assert_array_equal(inserted_point["point"], np.array([4, -1]))

    def test_insert_points(self):
        info1 = iter(_POLYLINE_INFO_1)
        info2 = iter(_POLYLINE_INFO_2)
        inserted_points_1 = Polyline2D._insert_points(info1, info2)
        inserted_points_2 = (
            [{"index": 2, "point": np.array([1.5, 2.0])}],
            [{"index": 1, "point": np.array([4.0, -1.0])}],
        )
        for points_1, points_2 in zip_longest(inserted_points_1, inserted_points_2):
            for point_1, point_2 in zip_longest(points_1, points_2):
                assert point_1["index"] == point_2["index"]
                np.testing.assert_array_equal(point_1["point"], point_2["point"])

    def test_max_distance_in_point_pairs(self):
        polyline_1 = np.array([[1, 1], [1, 2], [2, 2]])
        polyline_2 = np.array([[4, 5], [2, 1], [3, 3]])
        polyline_3 = np.array([[4, 5], [2, 1]])

        with pytest.raises(AssertionError):
            Polyline2D._max_distance_in_point_pairs(polyline_1, polyline_3)
        assert Polyline2D._max_distance_in_point_pairs(polyline_1, polyline_2) == 5.0

    def test_uniform_frechet_distance(self):
        polyline_1 = [[1, 1], [1, 2], [2, 2]]
        polyline_2 = [[4, 5], [2, 1], [3, 3]]
        assert Polyline2D.uniform_frechet_distance(polyline_1, polyline_2) == 3.605551275463989

    def test_similarity(self):
        polyline_1 = [[1, 1], [1, 2], [2, 2]]
        polyline_2 = [[4, 5], [2, 1], [3, 3]]
        assert Polyline2D.similarity(polyline_1, polyline_2) == 0.2788897449072022

    def test_loads(self):
        polyline = Polyline2D.loads(_POLYLINE_DATA)
        assert polyline == Polyline2D([Vector2D(1, 1), Vector2D(1, 2), Vector2D(2, 2)])

    def test_dumps(self):
        polyline = Polyline2D([[1, 1], [1, 2], [2, 2]])
        assert polyline.dumps() == _POLYLINE_DATA

    def test_bounds(self):
        polyline = Polyline2D([[1, 1], [1, 2], [2, 2]])
        assert polyline.bounds() == Box2D(1, 1, 2, 2)
