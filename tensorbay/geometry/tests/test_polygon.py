#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay.geometry.box import Box2D
from tensorbay.geometry.polygon import RLE, MultiPolygon, Polygon
from tensorbay.geometry.vector import Vector2D

_DATA_POLYGON = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 2.0}, {"x": 2.0, "y": 3.0}]
_DATA_MULTIPOLYGON = [
    [{"x": 1.0, "y": 4.0}, {"x": 2.0, "y": 3.7}, {"x": 7.0, "y": 4.0}],
    [{"x": 5.0, "y": 7.0}, {"x": 6.0, "y": 7.0}, {"x": 9.0, "y": 8.0}],
]
_DATA_RLE = [272, 2, 4, 4, 2, 9]


class TestPolygon:
    def test_init(self):
        sequence = [[1, 2], [2, 3], [2, 2]]
        assert Polygon(None) == Polygon([])
        assert Polygon(sequence) == Polygon([Vector2D(1, 2), Vector2D(2, 3), Vector2D(2, 2)])

    def test_eq(self):
        polygon_1 = Polygon([[1, 2], [2, 3], [2, 2]])
        polygon_2 = Polygon([[1, 2], [2, 3], [2, 2]])
        polygon_3 = Polygon([[1, 2], [3, 4], [2, 2]])
        assert (polygon_1 == polygon_2) == True
        assert (polygon_1 == polygon_3) == False

    def test_loads(self):
        polygon = Polygon.loads(_DATA_POLYGON)
        assert polygon._data == [Vector2D(1.0, 1.0), Vector2D(2.0, 2.0), Vector2D(2.0, 3.0)]

    def test_dumps(self):
        polygon = Polygon([[1, 1], [2, 2], [2, 3]])
        assert polygon.dumps() == _DATA_POLYGON

    def test_area(self):
        polygon = Polygon([[1, 2], [2, 2], [2, 3]])
        assert polygon.area() == 0.5

    def test_bounds(self):
        polygon = Polygon([[1, 2], [2, 4], [2, 3]])
        assert polygon.bounds() == Box2D(1, 2, 2, 4)


class TestMultiPolygon:
    def test_init(self):
        assert MultiPolygon(None) == MultiPolygon([])
        polygon1 = Polygon([[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]])
        polygon2 = Polygon([[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]])
        assert MultiPolygon(
            [[[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]], [[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]]
        ) == MultiPolygon([polygon1, polygon2])

    def test_loads(self):
        multipolygon = MultiPolygon.loads(_DATA_MULTIPOLYGON)
        assert multipolygon._data == [
            Polygon([[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]]),
            Polygon([[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]),
        ]

    def test_dumps(self):
        multipolygon = MultiPolygon(
            [[[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]], [[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]]
        )
        assert multipolygon.dumps() == _DATA_MULTIPOLYGON


class TestRLE:
    def test_init(self):
        assert RLE([272, 2, 4, 4, 2, 9])._data == [272, 2, 4, 4, 2, 9]

    def test_loads(self):
        rle = RLE.loads(_DATA_RLE)
        assert rle._data == _DATA_RLE

    def test_dumps(self):
        rle = RLE(_DATA_RLE)
        assert rle.dumps() == _DATA_RLE
