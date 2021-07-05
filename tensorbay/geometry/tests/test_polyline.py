#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from math import isclose

from .. import Box2D, MultiPolyline2D, Polyline2D, Vector2D

_POLYLINE_SEQUENCE_1 = [[1, 1], [2, 2], [4, 4], [5, 5]]
_POLYLINE_SEQUENCE_2 = [[2, 1], [4, 3], [6, 5]]

_POLYLINE_1 = Polyline2D(_POLYLINE_SEQUENCE_1)
_POLYLINE_2 = Polyline2D(_POLYLINE_SEQUENCE_2)

_MULTI_POLYLINE_SEQUENCE = [_POLYLINE_SEQUENCE_1, _POLYLINE_SEQUENCE_2]
_MULTI_POLYLINE = MultiPolyline2D([_POLYLINE_SEQUENCE_1, _POLYLINE_SEQUENCE_2])

_POLYLINE_INFO_1 = (
    {
        "index": 0,
        "point": Vector2D(1, 1),
        "vector": Vector2D(1, 1),
        "time": 0.25,
        "last_time": 0,
    },
    {
        "index": 1,
        "point": Vector2D(2, 2),
        "vector": Vector2D(2, 2),
        "time": 0.75,
        "last_time": 0.25,
    },
    {
        "index": 2,
        "point": Vector2D(4, 4),
        "vector": Vector2D(1, 1),
        "time": 1.0,
        "last_time": 0.75,
    },
)
_POLYLINE_INFO_2 = (
    {
        "index": 0,
        "point": Vector2D(2, 1),
        "vector": Vector2D(2, 2),
        "time": 0.5,
        "last_time": 0,
    },
    {
        "index": 1,
        "point": Vector2D(4, 3),
        "vector": Vector2D(2, 2),
        "time": 1.0,
        "last_time": 0.5,
    },
)

_POLYLINE_CONTENT_1 = [{"x": 1, "y": 1}, {"x": 2, "y": 2}, {"x": 4, "y": 4}, {"x": 5, "y": 5}]
_POLYLINE_CONTENT_2 = [{"x": 2, "y": 1}, {"x": 4, "y": 3}, {"x": 6, "y": 5}]
_MULTI_POLYLINE_CONTENT = [_POLYLINE_CONTENT_1, _POLYLINE_CONTENT_2]


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

    def test_get_polyline_info(self):
        assert _POLYLINE_INFO_1 == Polyline2D._get_polyline_info(_POLYLINE_1)
        assert _POLYLINE_INFO_2 == Polyline2D._get_polyline_info(_POLYLINE_2)

    def test_get_insert_arg(self):
        assert Polyline2D._get_insert_arg(0.2, _POLYLINE_INFO_1[0]) == (1, Vector2D(1.8, 1.8))
        assert Polyline2D._get_insert_arg(0.8, _POLYLINE_INFO_1[1]) == (2, Vector2D(4.2, 4.2))

    def test_get_insert_args(self):
        assert Polyline2D._get_insert_args(_POLYLINE_INFO_1, _POLYLINE_INFO_2) == (
            [(2, Vector2D(3.0, 3.0))],
            [(1, Vector2D(3.0, 2.0)), (2, Vector2D(5.0, 4.0))],
        )

    def test_uniform_frechet_distance(self):
        assert Polyline2D.uniform_frechet_distance(_POLYLINE_1, _POLYLINE_1) == 0
        assert Polyline2D.uniform_frechet_distance(_POLYLINE_2, _POLYLINE_2) == 0
        assert Polyline2D.uniform_frechet_distance(_POLYLINE_1, _POLYLINE_2) == 1
        assert Polyline2D.uniform_frechet_distance(_POLYLINE_SEQUENCE_1, _POLYLINE_SEQUENCE_2) == 1

    def test_similarity(self):
        assert Polyline2D.similarity(_POLYLINE_1, _POLYLINE_1) == 1
        assert Polyline2D.similarity(_POLYLINE_2, _POLYLINE_2) == 1
        assert isclose(Polyline2D.similarity(_POLYLINE_1, _POLYLINE_2), 0.8438262381113939)
        assert isclose(
            Polyline2D.similarity(_POLYLINE_SEQUENCE_1, _POLYLINE_SEQUENCE_2), 0.8438262381113939
        )

    def test_loads(self):
        assert Polyline2D.loads(_POLYLINE_CONTENT_1) == _POLYLINE_1
        assert Polyline2D.loads(_POLYLINE_CONTENT_2) == _POLYLINE_2

    def test_dumps(self):
        assert _POLYLINE_1.dumps() == _POLYLINE_CONTENT_1
        assert _POLYLINE_2.dumps() == _POLYLINE_CONTENT_2

    def test_bounds(self):
        assert _POLYLINE_1.bounds() == Box2D(1, 1, 5, 5)
        assert _POLYLINE_2.bounds() == Box2D(2, 1, 6, 5)


class TestMultiPolyline2D:
    def test_init(self):
        assert MultiPolyline2D() == MultiPolyline2D([])
        assert MultiPolyline2D(_MULTI_POLYLINE_SEQUENCE) == MultiPolyline2D(
            [
                [Vector2D(1, 1), Vector2D(2, 2), Vector2D(4, 4), Vector2D(5, 5)],
                [Vector2D(2, 1), Vector2D(4, 3), Vector2D(6, 5)],
            ]
        )

    def test_loads(self):
        assert MultiPolyline2D.loads(_MULTI_POLYLINE_CONTENT) == _MULTI_POLYLINE

    def test_dumps(self):
        assert _MULTI_POLYLINE.dumps() == _MULTI_POLYLINE_CONTENT

    def test_bounds(self):
        assert _MULTI_POLYLINE.bounds() == Box2D(1, 1, 6, 5)
