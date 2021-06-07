#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Polyline2D.

:class:`Polyline2D` contains the coordinates of the vertexes of the polyline
and provides a series of methods to operate on polyline, such as
:meth:`Polyline2D.uniform_frechet_distance` and :meth:`Polyline2D.similarity`.

"""

from itertools import accumulate, count, islice, product
from sys import version_info
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Type, TypeVar

from ..utility import common_loads
from .polygon import PointList2D
from .vector import Vector2D

if version_info >= (3, 8):
    from math import dist as _dist
else:
    from math import hypot

    def _dist(point1: Iterable[float], point2: Iterable[float]) -> float:  # type: ignore[misc]
        return hypot(*((p1 - p2) for p1, p2 in zip(point1, point2)))


class Polyline2D(PointList2D[Vector2D]):
    """This class defines the concept of Polyline2D.

    :class:`Polyline2D` contains the coordinates of the vertexes of the polyline
    and provides a series of methods to operate on polyline, such as
    :meth:`Polyline2D.uniform_frechet_distance` and :meth:`Polyline2D.similarity`.

    Examples:
        >>> Polyline2D([[1, 2], [2, 3]])
        Polyline2D [
          Vector2D(1, 2),
          Vector2D(2, 3)
        ]

    """

    _P = TypeVar("_P", bound="Polyline2D")

    _ElementType = Vector2D

    @staticmethod
    def _get_polyline_info(polyline: "Polyline2D") -> Tuple[Dict[str, Any], ...]:
        vectors = tuple(p1 - p2 for p1, p2 in zip(islice(polyline, 1, None), polyline))
        distances = tuple(accumulate(abs(v) for v in vectors))
        velocity = distances[-1]
        time = [d / velocity for d in distances]
        time.insert(0, 0)

        return tuple(
            {
                "index": index,
                "point": point,
                "vector": vector,
                "time": current_time,
                "last_time": last_time,
            }
            for index, vector, point, current_time, last_time in zip(
                count(), vectors, polyline, islice(time, 1, None), time
            )
        )

    @staticmethod
    def _get_insert_arg(time: float, info: Dict[str, Any]) -> Tuple[int, Vector2D]:
        ratio = (time - info["last_time"]) / (info["time"] - info["last_time"])
        insert_point = info["point"] + info["vector"] * ratio
        return (info["index"] + 1, insert_point)

    @staticmethod
    def _get_insert_args(
        polyline_info1: Iterable[Dict[str, Any]],
        polyline_info2: Iterable[Dict[str, Any]],
    ) -> Tuple[List[Tuple[int, Vector2D]], List[Tuple[int, Vector2D]]]:
        insert_points1: List[Tuple[int, Vector2D]] = []
        insert_points2: List[Tuple[int, Vector2D]] = []

        iter1 = iter(polyline_info1)
        iter2 = iter(polyline_info2)
        info1 = next(iter1)
        info2 = next(iter2)

        try:
            while True:
                time1 = info1["time"]
                time2 = info2["time"]
                if time1 < time2:
                    insert_points2.append(Polyline2D._get_insert_arg(time1, info2))
                    info1 = next(iter1)
                elif time1 > time2:
                    insert_points1.append(Polyline2D._get_insert_arg(time2, info1))
                    info2 = next(iter2)
                else:
                    info1 = next(iter1)
                    info2 = next(iter2)
        except StopIteration:
            pass

        return insert_points1, insert_points2

    @staticmethod
    def uniform_frechet_distance(
        polyline1: Sequence[Sequence[float]],
        polyline2: Sequence[Sequence[float]],
    ) -> float:
        """Compute the maximum distance between two curves if walk on a constant speed on a curve.

        Arguments:
            polyline1: The first polyline consists of multiple points.
            polyline2: The second polyline consists of multiple points.

        Returns:
            The computed distance between the two polylines.

        Examples:
            >>> polyline_1 = [[1, 1], [1, 2], [2, 2]]
            >>> polyline_2 = [[4, 5], [2, 1], [3, 3]]
            >>> Polyline2D.uniform_frechet_distance(polyline_1, polyline_2)
            3.605551275463989

        """
        # forward:
        line1 = Polyline2D(polyline1)
        line2 = Polyline2D(polyline2)

        polyline_info1 = Polyline2D._get_polyline_info(line1)
        polyline_info2 = Polyline2D._get_polyline_info(line2)

        insert_args1, insert_args2 = Polyline2D._get_insert_args(polyline_info1, polyline_info2)

        for arg in reversed(insert_args1):
            line1.insert(*arg)  # pylint: disable=no-member
        for arg in reversed(insert_args2):
            line2.insert(*arg)  # pylint: disable=no-member
        distance_forward = max(_dist(*args) for args in zip(line1, line2))

        # backward:
        line1 = Polyline2D(polyline1)
        line2_reverse = Polyline2D(reversed(polyline2))

        polyline_info2_reverse = Polyline2D._get_polyline_info(line2_reverse)

        insert_args1, insert_args2 = Polyline2D._get_insert_args(
            polyline_info1, polyline_info2_reverse
        )

        for arg in reversed(insert_args1):
            line1.insert(*arg)  # pylint: disable=no-member
        for arg in reversed(insert_args2):
            line2_reverse.insert(*arg)  # pylint: disable=no-member
        distance_reverse = max(_dist(*args) for args in zip(line1, line2_reverse))

        return min(distance_forward, distance_reverse)

    @staticmethod
    def similarity(
        polyline1: Sequence[Sequence[float]],
        polyline2: Sequence[Sequence[float]],
    ) -> float:
        """Calculate the similarity between two polylines, range from 0 to 1.

        Arguments:
            polyline1: The first polyline consists of multiple points.
            polyline2: The second polyline consisting of multiple points.

        Returns:
            The similarity between the two polylines.
            The larger the value, the higher the similarity.

        Examples:
            >>> polyline_1 = [[1, 1], [1, 2], [2, 2]]
            >>> polyline_2 = [[4, 5], [2, 1], [3, 3]]
            >>> Polyline2D.similarity(polyline_1, polyline_2)
            0.2788897449072022

        """
        min_distance = Polyline2D.uniform_frechet_distance(polyline1, polyline2)
        max_distance = max(_dist(*args) for args in product(polyline1, polyline2))
        return 1 - min_distance / max_distance

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`Polyline2D` from a list of dict.

        Arguments:
            contents: A list of dict containing
                the coordinates of the vertexes of the polyline.

        Returns:
            The loaded :class:`Polyline2D` object.

        Examples:
            >>> polyline = Polyline2D([[1, 1], [1, 2], [2, 2]])
            >>> polyline.dumps()
            [{'x': 1, 'y': 1}, {'x': 1, 'y': 2}, {'x': 2, 'y': 2}]

        """
        return common_loads(cls, contents)
