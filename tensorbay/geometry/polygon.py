#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""PointList2D, Polygon2D.

:class:`PointList2D` contains a list of 2D points.

:class:`Polygon` contains the coordinates of the vertexes of the polygon
and provides :meth:`Polygon2D.area` to calculate the area of the polygon.

"""

from typing import Dict, Iterable, List, Optional, Type, TypeVar

from ..utility import UserMutableSequence, common_loads
from .box import Box2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class PointList2D(UserMutableSequence[_T]):
    """This class defines the concept of PointList2D.

    :class:`PointList2D` contains a list of 2D points.

    Arguments:
        points: A list of 2D points.

    """

    _P = TypeVar("_P", bound="PointList2D[_T]")

    _ElementType: Type[_T]

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
    ) -> None:
        self._data = []
        if points is None:
            return

        for point in points:
            self._data.append(self._ElementType(*point))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._data.__eq__(other._data)

    def _loads(self: _P, contents: List[Dict[str, float]]) -> None:
        self._data = []
        for point in contents:
            self._data.append(self._ElementType.loads(point))

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`PointList2D` from a list of dictionaries.

        Arguments:
            contents: A list of dictionaries containing the coordinates of the vertexes
                of the polygon::

                    [
                        {
                            "x": ...
                            "y": ...
                        },
                        ...
                    ]

        Returns:
            The loaded :class:`PointList2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> List[Dict[str, float]]:
        """Dumps a :class:`PointList2D` into a point list.

        Returns:
            A list of dictionaries containing the coordinates of the vertexes
            of the polygon within the point list.

        """
        return [point.dumps() for point in self._data]

    def bounds(self) -> Box2D:
        """Calculate the bounds of point list.

        Returns:
            The bounds of point list.

        """
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
    """This class defines the concept of Polygon2D.

    :class:`Polygon2D` contains the coordinates of the vertexes of the polygon and provides
    :meth:`Polygon2D.area` to calculate the area of the polygon.

    Examples:
        >>> Polygon2D([[1, 2], [2, 3], [2, 2]])
        Polygon2D [
          Vector2D(1, 2),
          Vector2D(2, 3),
          Vector2D(2, 2)
        ]

    """

    _P = TypeVar("_P", bound="Polygon2D")

    _ElementType = Vector2D

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`Polygon2D` from a list of dictionaries.

        Arguments:
            contents: A list of dictionaries containing the coordinates
                of the vertexes of the polygon.

        Returns:
            The loaded :class:`Polygon2D` object.

        Examples:
            >>> contents = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 2.0}, {"x": 2.0, "y": 3.0}]
            >>> Polygon2D.loads(contents)
            Polygon2D [
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
            >>> polygon = Polygon2D([[1, 2], [2, 2], [2, 3]])
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
