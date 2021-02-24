#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class Basic, Vector, Vector2D, Vector3D.
"""

from typing import Dict, Iterable, Optional, Sequence, Tuple, Type, TypeVar, Union

from ..utility import ReprType, UserSequence, common_loads

_T = TypeVar("_T", bound="Vector")


class Vector(UserSequence[float]):
    """A class used as base class of Vector2D and Vector3D, extending the :class `Sequence`.

    :param args: Coordinates of the vector
    :param kwargs: float
        vector2d = Vector(x=1, y=2)
        vector3d = Vector(x=1, y=2, z=3)
    :raises ValueError: When the dimension of the input parameters is not correct
    :return: The created Vector2D or Vector3D class
    """

    _DIMENSION: Optional[int] = None

    _data: Tuple[float, ...]
    _repr_type = ReprType.INSTANCE

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
        if kwargs:
            return cls.loads(kwargs)

        data = cls._process_args(*args)

        ReturnType: Type["Vector"] = cls
        if len(data) == Vector2D._DIMENSION:
            ReturnType = Vector2D
        elif len(data) == Vector3D._DIMENSION:
            ReturnType = Vector3D
        else:
            raise ValueError("Require 2 or 3 dimensional data to construct a Vector.")

        obj: _T = object.__new__(ReturnType)
        obj._data = data
        return obj

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a Vector from a dict containing coordinates of the vector.

        :param contents: A dictionary containing coordinates of a vector
        {
            "x": ...
            "y": ...
        }
        or
        {
            "x": ...
            "y": ...
            "z": ...
        }
        :return: The loaded Vector2D or Vector3D
        """
        if "z" in contents:
            return Vector3D.loads(contents)  # type: ignore[return-value]
        return Vector2D.loads(contents)  # type: ignore[return-value]

    def _repr_head(self) -> str:
        return f"{self.__class__.__name__}{self._data}"

    def __add__(self, other: Sequence[float]) -> _T:
        """Calculate the sum of vector and other sequence.

        :raises ValueError: When the vectors to be added have different dimensions
        :returns: The sum vector of adding two vectors
        """
        if not isinstance(other, Sequence):  # pylint: disable=W1116
            return NotImplemented

        if len(self._data) != len(other):
            raise ValueError("Vectors to be added must have the same dimension")
        result: _T = object.__new__(self.__class__)
        result._data = tuple(i + j for i, j in zip(self._data, other))
        return result

    def __radd__(self, other: Sequence[float]) -> _T:
        """Calculate the sum of other sequence and the vector.

        :returns: The sum vector of adding two vectors
        """
        return self.__add__(other)

    def __neg__(self) -> _T:
        result: _T = object.__new__(self.__class__)
        result._data = tuple(-coordinate for coordinate in self._data)
        return result

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)

        return False

    @staticmethod
    def _process_args(*args: Union[None, float, Iterable[float]]) -> Tuple[float, ...]:
        data: Optional[Iterable[float]]
        data = args[0] if len(args) == 1 else args  # type: ignore[assignment]
        if not data:
            return ()

        try:
            return tuple(data)
        except TypeError as error:
            raise TypeError("Require 2 or 3 dimensional data to construct a vector.") from error


class Vector2D(Vector):
    """A class used to represent 2D vector extending the :class `Vector`."""

    _DIMENSION = 2

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
        if not data:
            obj._data = (0.0, 0.0)
            return obj

        try:
            x, y = data
            obj._data = (x, y)
            return obj
        except (ValueError, TypeError) as error:
            raise TypeError(
                f"Require {cls._DIMENSION} dimensional data to construct {cls.__name__}."
            ) from error

    def _loads(self: _T, contents: Dict[str, float]) -> None:
        self._data = (contents["x"], contents["y"])

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a Vector2D from a dict containing coordinates of the 2D vector.

        :param contents: A dictionary containing coordinates of a 2D vector
        {
            "x": ...
            "y": ...
        }
        :return: The loaded Vector2D
        """
        return common_loads(cls, contents)

    @property
    def x(self) -> float:
        """Returns the x coordinate of the vector.

        :return: x coordinate in float type
        """
        return self._data[0]

    @property
    def y(self) -> float:

        """Returns the y coordinate of the vector.

        :return: y coordinate in float type
        """
        return self._data[1]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector as a dictionary.

        :return: A dictionary containing the vector coordinate.
        """
        return {"x": self._data[0], "y": self._data[1]}


class Vector3D(Vector):
    """A class used to represent 3D vector extending the :class `Vector`."""

    _DIMENSION = 3

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
        if not data:
            obj._data = (0.0, 0.0, 0.0)
            return obj

        try:
            x, y, z = data
            obj._data = (x, y, z)
            return obj
        except (ValueError, TypeError) as error:
            raise TypeError(
                f"Require {cls._DIMENSION} dimensional data to construct {cls.__name__}."
            ) from error

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a Vector3D from a dict containing coordinates of the 3D vector.

        :param contents: A dictionary containing coordinates of a 3D vector
        {
            "x": ...
            "y": ...
            "z": ...
        }
        :return: The loaded Vector3D
        """
        return common_loads(cls, contents)

    def _loads(self: _T, contents: Dict[str, float]) -> None:
        self._data = (contents["x"], contents["y"], contents["z"])

    @property
    def x(self) -> float:

        """Returns the x coordinate of the vector.

        :return: x coordinate in float type
        """
        return self._data[0]

    @property
    def y(self) -> float:

        """Returns the y coordinate of the vector.

        :return: y coordinate in float type
        """
        return self._data[1]

    @property
    def z(self) -> float:

        """Returns the z coordinate of the vector.

        :return: z coordinate in float type
        """
        return self._data[2]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector as a dictionary.

        :return: A dictionary containing the vector coordinate.
        """
        return {"x": self._data[0], "y": self._data[1], "z": self._data[2]}
