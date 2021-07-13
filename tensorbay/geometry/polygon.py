#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""PointList2D, Polygon.

:class:`PointList2D` contains a list of 2D points.

:class:`Polygon` contains the coordinates of the vertexes of the polygon
and provides :meth:`Polygon.area` to calculate the area of the polygon.

"""

from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

from ..utility import UserMutableSequence, common_loads
from .box import Box2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class PointList2D(UserMutableSequence[_T]):  # pylint: disable=too-many-ancestors
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

    def _loads(self: _P, contents: List[Dict[str, float]]) -> None:
        self._data = []
        for point in contents:
            self._data.append(self._ElementType.loads(point))

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`PointList2D` from a list of dictionaries.

        Arguments:
            contents: A list of dictionaries containing the coordinates of the vertexes
                of the point list::

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


_L = TypeVar("_L", bound=PointList2D[Any])


class MultiPointList2D(UserMutableSequence[_L]):  # pylint: disable=too-many-ancestors
    """This class defines the concept of MultiPointList2D.

    :class:`MultiPointList2D` contains multiple 2D point lists.

    Arguments:
        point_lists: A list of 2D point list.

    """

    _P = TypeVar("_P", bound="MultiPointList2D[_L]")

    _ElementType: Type[_L]

    def __init__(self, point_lists: Optional[Iterable[Iterable[Iterable[float]]]] = None) -> None:
        self._data = (
            [self._ElementType(point_list) for point_list in point_lists] if point_lists else []
        )

    def _loads(self: _P, contents: List[List[Dict[str, float]]]) -> None:
        self._data = [self._ElementType.loads(point_list) for point_list in contents]

    def _dumps(self) -> List[List[Dict[str, float]]]:
        return [point_list.dumps() for point_list in self._data]

    @classmethod
    def loads(cls: Type[_P], contents: List[List[Dict[str, float]]]) -> _P:
        """Loads a :class:`MultiPointList2D` from the given contents.

        Arguments:
            contents: A list of dictionary lists containing the coordinates of the vertexes
                of the multiple point lists::

                    [
                        [
                            {
                                "x": ...
                                "y": ...
                            },
                            ...
                        ]
                        ...
                    ]

        Returns:
            The loaded :class:`MultiPointList2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> List[List[Dict[str, float]]]:
        """Dumps all the information of the :class:`MultiPointList2D`.

        Returns:
            All the information of the :class:`MultiPointList2D`.

        """
        return self._dumps()

    def bounds(self) -> Box2D:
        """Calculate the bounds of multiple point lists.

        Returns:
            The bounds of multiple point lists.

        """
        x_min = x_max = self._data[0][0].x
        y_min = y_max = self._data[0][0].y

        for points in self._data:
            box = points.bounds()
            if box.xmin < x_min:
                x_min = box.xmin
            elif box.xmax > x_max:
                x_max = box.xmax

            if box.ymin < y_min:
                y_min = box.ymin
            elif box.ymax > y_max:
                y_max = box.ymax

        return Box2D(x_min, y_min, x_max, y_max)


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
