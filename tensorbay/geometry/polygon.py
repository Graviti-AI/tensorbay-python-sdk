#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Polygon.

:class:`Polygon` contains the coordinates of the vertexes of the polygon
and provides :meth:`Polygon.area` to calculate the area of the polygon.

"""

from typing import Dict, List, Type, TypeVar

from ..utility import common_loads
from .point_list import PointList2D
from .vector import Vector2D


class Polygon(PointList2D[Vector2D]):  # pylint: disable=too-many-ancestors
    """This class defines the concept of Polygon.

    :class:`Polygon` contains the coordinates of the vertexes of the polygon and provides
    :meth:`Polygon.area` to calculate the area of the polygon.

    Examples:
        >>> Polygon([[1, 2], [2, 3], [2, 2]])
        Polygon [
          Vector2D(1, 2),
          Vector2D(2, 3),
          Vector2D(2, 2)
        ]

    """

    _P = TypeVar("_P", bound="Polygon")

    _ElementType = Vector2D

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Loads the information of :class:`Polygon`.

        Arguments:
            contents: A list of dictionary lists containing the coordinates
                of the vertexes of the polygon.

        Returns:
            The loaded :class:`Polygon` object.

        Examples:
            >>> contents = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 2.0}, {"x": 2.0, "y": 3.0}]
            >>> Polygon.loads(contents)
            Polygon [
              Vector2D(1.0, 1.0),
              Vector2D(2.0, 2.0),
              Vector2D(2.0, 3.0)
            ]

        """
        return common_loads(cls, contents)

    def area(self) -> float:
        """Return the area of the polygon.

        The area is positive if the rotating direction of the points is counterclockwise,
        and negative if clockwise.

        Returns:
            The area of the polygon.

        Examples:
            >>> polygon = Polygon([[1, 2], [2, 2], [2, 3]])
            >>> polygon.area()
            0.5

        """
        area = 0.0
        for i in range(len(self._data)):
            # pylint: disable=invalid-name
            x1, y1 = self._data[i - 1]
            x2, y2 = self._data[i]
            area += x1 * y2 - x2 * y1
        return area / 2
