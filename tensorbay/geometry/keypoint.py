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

from typing import Dict, Iterable, List, Optional, Sequence, Type, TypeVar, Union

from ..utility import common_loads
from .polygon import PointList2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class Keypoint2D(Vector2D):
    """This class defines the concept of Keypoint2D.

    :class:`Keypoint2D` contains the information of 2D keypoint,
    such as the coordinates and visible status(optional).

    Arguments:
        *args: Coordinates and visible status(optional) of the 2D keypoint.
        **kwargs: Coordinates are of float type and visible status is of int type:

            .. code:: python

                keypoint2d = Keypoint2D(x=1.0, y=2.0)
                keypoint2d = Keypoint2D(x=1.0, y=2.0, v=0)
                keypoint2d = Keypoint2D(x=1.0, y=2.0, v=1)
                keypoint2d = Keypoint2D(x=1.0, y=2.0, v=2)

            Visible status can be "BINARY" or "TERNARY":

            +---------------+---------+-----------+-----------+
            | Visual Status | v = 0   | v = 1     | v = 2     |
            +===============+=========+===========+===========+
            | BINARY        | visible | invisible |           |
            +---------------+---------+-----------+-----------+
            | TERNARY       | visible | occluded  | invisible |
            +---------------+---------+-----------+-----------+

    Raises:
        TypeError: If input parameters do not meet the requirement.

    """

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
        """Create a new instance of :class:`Keypoint2D`.

        Arguments:
            *args: Coordinates and visible status(optional) of the 2D keypoint.
            **kwargs: Coordinates are of float type and visible status is of int type:

                .. code:: python

                    keypoint2d = Keypoint2D(x=1.0, y=2.0)
                    keypoint2d = Keypoint2D(x=1.0, y=2.0, v=0)
                    keypoint2d = Keypoint2D(x=1.0, y=2.0, v=1)
                    keypoint2d = Keypoint2D(x=1.0, y=2.0, v=2)

        Raises:
            TypeError: If input parameters do not meet the requirement.

        Returns:
            The created :class:`Keypoint2D` object.

        """
        if kwargs:
            return cls.loads(kwargs)

        obj: _T = object.__new__(cls)
        data: Optional[Iterable[float]]
        data = args[0] if len(args) == 1 else args  # type: ignore[assignment]

        data = tuple(data)  # type: ignore[arg-type]
        if len(data) not in (2, 3):
            raise TypeError(f"Require two or three dimensional data to construct {cls.__name__}.")

        obj._data = data
        return obj

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a :class:`Keypoint2D` from a dict containing coordinates of a 2D keypoint.

        Arguments:
            contents: A dict containing coordinates and visible status(optional)
                of a 2D keypoint::

                    {
                        "x": ...
                        "y": ...
                        "v": ...
                    }

        Returns:
            The loaded :class:`Keypoint2D` object.

        """
        return common_loads(cls, contents)

    def _loads(self: _T, contents: Dict[str, float]) -> None:
        if "v" in contents:
            self._data = (contents["x"], contents["y"], contents["v"])
        else:
            self._data = (contents["x"], contents["y"])

    def __add__(self, other: Sequence[float]) -> Vector2D:  # type: ignore[override]
        # Result of adding Keypoint2D with another sequence should be a Vector2D.
        # Add function of Vector2D should also add support for adding with a Keypoint2D.
        # Will be implemented in the future.
        return NotImplemented

    def __neg__(self) -> Vector2D:  # type: ignore[override]
        result: Vector2D = object.__new__(Vector2D)
        result._data = tuple(-coordinate for coordinate in self._data[: self._DIMENSION])
        return result

    @property
    def v(self) -> Optional[int]:  # pylint: disable=invalid-name
        """Return the visible status of the 2D keypoint.

        Returns:
            Visible status of the 2D keypoint.

        """
        if len(self._data) != self._DIMENSION:
            return self._data[2]  # type: ignore[return-value]
        return None

    def dumps(self) -> Dict[str, float]:
        """Dumps the :class:`Keypoint2D` into a dict.

        Returns:
            A dict containing coordinates and visible status(optional) of the 2D keypoint.

        """
        contents = {"x": self._data[0], "y": self._data[1]}
        if len(self._data) != self._DIMENSION:
            contents["v"] = self._data[2]
        return contents


class Keypoints2D(PointList2D[Keypoint2D]):
    """This class defines the concept of Keypoints2D.

    :class:`Keypoints2D` contains a list of 2D keypoint and is based on
    :class:`~tensorbay.geometry.polygon.PointList2D`.

    """

    _ElementType = Keypoint2D
    _P = TypeVar("_P", bound="Keypoints2D")

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a :class:`Keypoints2D` from a list of dict.

        Arguments:
            contents: A list of dictionaries containing 2D keypoint::

                [
                    {
                        "x": ...
                        "y": ...
                        "v": ...           --- optional
                    },
                    ...
                ]

        Returns:
            The loaded :class:`Keypoints2D` object.

        """
        return common_loads(cls, contents)
