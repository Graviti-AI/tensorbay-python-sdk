#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Polygon.

:class:`Polygon` contains the coordinates of the vertexes of the polygon
and provides :meth:`Polygon.area` to calculate the area of the polygon.

"""

from typing import Dict, Iterable, List, Optional, Type, TypeVar

from ..utility import UserMutableSequence, common_loads
from .point_list import MultiPointList2D, PointList2D
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


class MultiPolygon(MultiPointList2D[Polygon]):  # pylint: disable=too-many-ancestors
    """This class defines the concept of MultiPolygon.

    :class:`MultiPolygon` contains a list of polygons.

    Arguments:
        polygons: A list of polygons.

    Examples:
        >>> MultiPolygon([[[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]],
        ...               [[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]])
        MultiPolygon [
            Polygon [...]
            Polygon [...]
            ...
        ]

    """

    _P = TypeVar("_P", bound="MultiPolygon")
    _ElementType = Polygon

    def __init__(self, polygons: Optional[Iterable[Iterable[Iterable[float]]]]):
        super().__init__(polygons)

    @classmethod
    def loads(cls: Type[_P], contents: List[List[Dict[str, float]]]) -> _P:
        """Loads a :class:`MultiPolygon` from the given contents.

        Arguments:
            contents: A list of dict lists containing
                the coordinates of the vertices of the polygon list.

        Returns:
            The loaded :class:`MultiPolyline2D` object.

        Examples:
            >>> contents = [[{'x': 1.0, 'y': 4.0}, {'x': 2.0, 'y': 3.7}, {'x': 7.0, 'y': 4.0}],
            ...             [{'x': 5.0, 'y': 7.0}, {'x': 6.0, 'y': 7.0}, {'x': 9.0, 'y': 8.0}]]
            >>> multipolygon = MultiPolygon.loads(contents)
            >>> multipolygon
            MultiPolygon [
                Polygon [...]
                Polygon [...]
                ...
            ]

        """
        return common_loads(cls, contents)

    def dumps(self) -> List[List[Dict[str, float]]]:
        """Dumps a :class:`MultiPolygon` into a polygon list.

        Returns:
            All the information of the :class:`MultiPolygon`.

        Examples:
            >>> multipolygon = MultiPolygon([[[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]],
            ...                             [[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]])
            >>> multipolygon.dumps()
            [
                [{'x': 1.0, 'y': 4.0}, {'x': 2.0, 'y': 3.7}, {'x': 7.0, 'y': 4.0}],
                [{'x': 5,0, 'y': 7.0}, {'x': 6.0, 'y': 7.0}, {'x': 9.0, 'y': 8.0}]
            ]

        """
        return self._dumps()


class RLE(UserMutableSequence[int]):
    """This class defines the concept of RLE.

    :class:`RLE` contains an rle format mask.

    Arguments:
        rle: A rle format mask.

    Examples:
        >>> RLE([272, 2, 4, 4, 2, 9])
        RLE [
          272,
          2,
          ...
        ]

    """

    _data: List[int]

    def __init__(self, rle: Optional[Iterable[int]]):
        self._data = list(rle) if rle else []

    def _dumps(self) -> List[int]:
        return self._data

    def _loads(self, contents: List[int]) -> None:
        self._data = contents

    @classmethod
    def loads(cls: Type["RLE"], contents: List[int]) -> "RLE":
        """Loads a :class:RLE` from the given contents.

        Arguments:
            contents: One rle mask.

        Returns:
            The loaded :class:`RLE` object.

        Examples:
            >>> contents = [272, 2, 4, 4, 2, 9]
            >>> rle = RLE.loads(contents)
            >>> rle
            RLE [
              272,
              2,
              ...
            ]

        """
        return common_loads(cls, contents)

    def dumps(self) -> List[int]:
        """Dumps a :class:`RLE` into one rle mask.

        Returns:
            All the information of the :class:`RLE`.

        Examples:
            >>> rle = RLE([272, 2, 4, 4, 2, 9])
            >>> rle.dumps()
            [272, 2, 4, 4, 2, 9]

        """
        return self._dumps()
