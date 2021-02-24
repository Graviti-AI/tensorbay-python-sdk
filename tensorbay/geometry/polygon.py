#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class PointList2D, Polygon2D"""

from typing import Dict, Iterable, List, Optional, Type, TypeVar

from ..utility import UserMutableSequence, common_loads
from .box import Box2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class PointList2D(UserMutableSequence[_T]):
    """this class defines the concept of point list

    :param points: a list of 2D point list
    """

    _ElementType: Type[_T]
    _P = TypeVar("_P", bound="PointList2D[_T]")

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
    ) -> None:
        self._data = []
        if points is None:
            return

        for point in points:
            self._data.append(self._ElementType(point))

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a PointList2D from a list of dict containing coordinates of 2D vectors
            within the pointlist.

        :param contents: A list of dict containing coordinates of 2D vectors within the pointlist
        [
            {
                "x": ...
                "y": ...
            },
            ...
        ]
        :return: The loaded PointList2D
        """
        return common_loads(cls, contents)

    def _loads(self: _P, contents: List[Dict[str, float]]) -> None:
        self._data = []
        for point in contents:
            self._data.append(self._ElementType.loads(point))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return False

    def dumps(self) -> List[Dict[str, float]]:
        """dump a PointList2D into a point list."""

        return [point.dumps() for point in self._data]

    def bounds(self) -> Box2D:
        """calculate the bounds of point list."""

        x_min = x_max = self._data[0].x
        y_min = y_max = self._data[0].y

        for point in self._data:
            if point.x < x_min:
                x_min = point.x
            elif point.x > x_max:
                x_max = point.x

            if point.y < y_min:
                y_min = point.y
            elif point.y > y_max:
                y_max = point.y

        return Box2D(x_min, y_min, x_max, y_max)


class Polygon2D(PointList2D[Vector2D]):
    """this class defines the concept of Polygon2D based on class PointList2D"""

    _ElementType = Vector2D
    _P = TypeVar("_P", bound="Polygon2D")

    def area(self) -> float:
        """Get the area of the polygon.
        If the orientation of the points is counterclockwise, the area is positive.
        If it is clockwise, the area is negative.

        :return: The area of the polygon
        """
        area = 0.0
        for i in range(len(self._data)):
            # pylint: disable=invalid-name
            x1, y1 = self._data[i - 1]
            x2, y2 = self._data[i]
            area += x1 * y2 - x2 * y1
        return area / 2

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a Polygon2D from a list of dict containing coordinates of 2D vectors
            within the 2D polygon.

        :param contents: A list of dict containing coordinates of 2D vectors within the polygon
        [
            {
                "x": ...
                "y": ...
            },
            ...
        ]
        :return: The loaded Polygon2D
        """
        return common_loads(cls, contents)
