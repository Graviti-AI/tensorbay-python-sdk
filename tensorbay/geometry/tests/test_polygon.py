#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Box2D, Polygon2D, Vector2D

_DATA_POLYGON2D = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 2.0}, {"x": 2.0, "y": 3.0}]


class TestPolygon2D:
    def test_init(self):
        sequence = [[1, 2], [2, 3], [2, 2]]
        assert Polygon2D(None) == Polygon2D([])
        assert Polygon2D(sequence) == Polygon2D([Vector2D(1, 2), Vector2D(2, 3), Vector2D(2, 2)])

    def test_eq(self):
        polygon_1 = Polygon2D([[1, 2], [2, 3], [2, 2]])
        polygon_2 = Polygon2D([[1, 2], [2, 3], [2, 2]])
        polygon_3 = Polygon2D([[1, 2], [3, 4], [2, 2]])
        assert (polygon_1 == polygon_2) == True
        assert (polygon_1 == polygon_3) == False

    def test_loads(self):
        polygon = Polygon2D.loads(_DATA_POLYGON2D)
        assert polygon._data == [Vector2D(1.0, 1.0), Vector2D(2.0, 2.0), Vector2D(2.0, 3.0)]

    def test_dumps(self):
        polygon = Polygon2D([[1, 1], [2, 2], [2, 3]])
        assert polygon.dumps() == _DATA_POLYGON2D

    def test_area(self):
        polygon = Polygon2D([[1, 2], [2, 2], [2, 3]])
        assert polygon.area() == 0.5

    def test_bounds(self):
        polygon = Polygon2D([[1, 2], [2, 4], [2, 3]])
        assert polygon.bounds() == Box2D(1, 2, 2, 4)
