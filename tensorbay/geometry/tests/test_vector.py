#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#

"""This file defines class TestVector"""

import pytest

from .. import Vector, Vector2D, Vector3D

_DATA = [{"x": 1.0, "y": 2.0}, {"x": 1.0, "y": 2.0, "z": 3.0}]


class TestVector:
    """Test Vector class."""

    def test_new_class(self) -> None:
        with pytest.raises(TypeError):
            Vector(1)
        with pytest.raises(ValueError):
            Vector(1, 2, 3, 4)
        assert Vector(1, 2) == Vector2D(1, 2)
        assert Vector(1, 2, 3) == Vector3D(1, 2, 3)

    @pytest.mark.parametrize("loads", _DATA)
    def test_loads_and_dumps(self, loads) -> None:
        vector = Vector.loads(loads)
        assert vector.dumps() == loads

    def test_add(self) -> None:
        vector_2d = Vector(1, 2)
        vector_3d = Vector(1, 2, 3)
        with pytest.raises(ValueError):
            vector_2d + vector_3d
        assert Vector(1, 1) + Vector(1, 1) == Vector(2, 2)
        assert Vector(1, 1, 1) + Vector(1, 1, 1) == Vector(2, 2, 2)
