#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Keypoints2D, Keypoint2D.

:class:`Keypoint2D` contains the information of 2D keypoint,
such as the coordinates and visible status(optional).

:class:`Keypoints2D` contains a list of 2D keypoint and is based on
:class:`~tensorbay.geometry.polygon.PointList2D`.

"""

from typing import Dict, Iterable, List, Optional, Type, TypeVar

from ..utility import common_loads
from .point_list import PointList2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class Keypoint2D(Vector2D):
    """This class defines the concept of Keypoint2D.

    :class:`Keypoint2D` contains the information of 2D keypoint,
    such as the coordinates and visible status(optional).

    Arguments:
        x: The x coordinate of the 2D keypoint.
        y: The y coordinate of the 2D keypoint.
        v: The visible status(optional) of the 2D keypoint.

            Visible status can be "BINARY" or "TERNARY":

            +---------------+---------+-----------+-----------+
            | Visual Status | v = 0   | v = 1     | v = 2     |
            +===============+=========+===========+===========+
            | BINARY        | visible | invisible |           |
            +---------------+---------+-----------+-----------+
            | TERNARY       | visible | occluded  | invisible |
            +---------------+---------+-----------+-----------+

    Examples:
        *Initialization Method 1:* Init from coordinates of x, y.

        >>> Keypoint2D(1.0, 2.0)
        Keypoint2D(1.0, 2.0)

        *Initialization Method 2:* Init from coordinates and visible status.

        >>> Keypoint2D(1.0, 2.0, 0)
        Keypoint2D(1.0, 2.0, 0)

    """

    def __init__(  # pylint: disable=super-init-not-called
        self, x: float, y: float, v: Optional[int] = None
    ) -> None:
        self._data = (x, y, v) if v is not None else (x, y)

    def __neg__(self) -> Vector2D:  # type: ignore[override]
        result: Vector2D = object.__new__(Vector2D)
        result._data = tuple(-coordinate for coordinate in self._data[: self._DIMENSION])
        return result

    def __add__(self, other: Iterable[float]) -> Vector2D:  # type: ignore[override]
        # Result of adding Keypoint2D with another sequence should be a Vector2D.
        # Add function of Vector2D should also add support for adding with a Keypoint2D.
        # Will be implemented in the future.
        return NotImplemented

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a :class:`Keypoint2D` from a dict containing coordinates of a 2D keypoint.

        Arguments:
            contents: A dict containing coordinates and visible status(optional)
                of a 2D keypoint.

        Returns:
            The loaded :class:`Keypoint2D` object.

        Examples:
            >>> contents = {"x":1.0,"y":2.0,"v":1}
            >>> Keypoint2D.loads(contents)
            Keypoint2D(1.0, 2.0, 1)

        """
        return cls(**contents)

    @property
    def v(self) -> Optional[int]:  # pylint: disable=invalid-name
        """Return the visible status of the 2D keypoint.

        Returns:
            Visible status of the 2D keypoint.

        Examples:
            >>> keypoint = Keypoint2D(3.0, 2.0, 1)
            >>> keypoint.v
            1

        """
        if len(self._data) != self._DIMENSION:
            return self._data[2]  # type: ignore[return-value]
        return None

    def dumps(self) -> Dict[str, float]:
        """Dumps the :class:`Keypoint2D` into a dict.

        Returns:
            A dict containing coordinates and visible status(optional) of the 2D keypoint.

        Examples:
            >>> keypoint = Keypoint2D(1.0, 2.0, 1)
            >>> keypoint.dumps()
            {'x': 1.0, 'y': 2.0, 'v': 1}

        """
        contents = {"x": self._data[0], "y": self._data[1]}
        if len(self._data) != self._DIMENSION:
            contents["v"] = self._data[2]
        return contents


class Keypoints2D(PointList2D[Keypoint2D]):
    """This class defines the concept of Keypoints2D.

    :class:`Keypoints2D` contains a list of 2D keypoint and is based on
    :class:`~tensorbay.geometry.polygon.PointList2D`.

    Examples:
        >>> Keypoints2D([[1, 2], [2, 3]])
        Keypoints2D [
          Keypoint2D(1, 2),
          Keypoint2D(2, 3)
        ]

    """

    _P = TypeVar("_P", bound="Keypoints2D")

    _ElementType = Keypoint2D

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`Keypoints2D` from a list of dict.

        Arguments:
            contents: A list of dictionaries containing 2D keypoint.

        Returns:
            The loaded :class:`Keypoints2D` object.

        Examples:
            >>> contents = [{"x": 1.0, "y": 1.0, "v": 1}, {"x": 2.0, "y": 2.0, "v": 2}]
            >>> Keypoints2D.loads(contents)
            Keypoints2D [
              Keypoint2D(1.0, 1.0, 1),
              Keypoint2D(2.0, 2.0, 2)
            ]

        """
        return common_loads(cls, contents)
