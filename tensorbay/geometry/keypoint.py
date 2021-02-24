#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class Keypoints2D and Keypoint2D."""

from typing import Dict, Iterable, List, Optional, Sequence, Type, TypeVar, Union

from ..utility import common_loads
from .polygon import PointList2D
from .vector import Vector2D

_T = TypeVar("_T", bound=Vector2D)


class Keypoint2D(Vector2D):
    """A class used to represent 2D keypoint.

    :param args: coordinates and visible status(optional) of the 2D keypoint
    :param kwargs: coordinates are float type and visible status is int type
        keypoint2d = Keypoint2D(x=1.0, y=2.0)
        keypoint2d = Keypoint2D(x=1.0, y=2.0, v=0)
        keypoint2d = Keypoint2D(x=1.0, y=2.0, v=1)
        keypoint2d = Keypoint2D(x=1.0, y=2.0, v=2)
    :raise TypeError: when input params do not meet the requirement
    """

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
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
        """Load a Keypoint2D from a dict containing coordinates of the 2D keypoint.

        :param contents: A dicitionary containing coordinates and visible status(optional)
                    of a 2D keypoint
        {
            "x": ...
            "y": ...
            "v": ...
        }
        :return: The loaded Keypoint2D
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
        """Get the visible status of the 2D keypoint.

        :return: visible status of the 2D keypoint
        """
        if len(self._data) != self._DIMENSION:
            return self._data[2]  # type: ignore[return-value]
        return None

    def dumps(self) -> Dict[str, float]:
        """Dumps the Keypoint2D into a dictionary.

        :return: a dictionary containing the 2D keypoint coordinates and visible status(optional)
        """
        contents = {"x": self._data[0], "y": self._data[1]}
        if len(self._data) != self._DIMENSION:
            contents["v"] = self._data[2]
        return contents


class Keypoints2D(PointList2D[Keypoint2D]):
    """A class used to represent 2D keypoints based on :class `PointList2D`."""

    _ElementType = Keypoint2D
    _P = TypeVar("_P", bound="Keypoints2D")

    @classmethod
    def loads(cls: Type[_P], contents: List[Dict[str, float]]) -> _P:
        """Load a Keypoints2D from a list of dict containing 2D keypoint within the 2D keypoints.

        :param contents: A list of dict containing 2D keypoint within the 2D keypoints
        [
            {
                "x": ...
                "y": ...
                "v": ...           --- optional
            },
            ...
        ]
        :return: The loaded Keypoints2D
        """
        return common_loads(cls, contents)
