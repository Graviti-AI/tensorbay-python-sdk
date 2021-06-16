#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Vector, Vector2D, Vector3D.

:class:`Vector` is the base class of :class:`Vector2D` and :class:`Vector3D`. It contains the
coordinates of a 2D vector or a 3D vector.

:class:`Vector2D` contains the coordinates of a 2D vector, extending :class:`Vector`.

:class:`Vector3D` contains the coordinates of a 3D vector, extending :class:`Vector`.

"""

from itertools import zip_longest
from math import hypot, sqrt
from sys import version_info
from typing import Dict, Iterable, Optional, Sequence, Tuple, Type, TypeVar, Union

from ..utility import ReprType, UserSequence

if version_info >= (3, 8):
    # math.hypot method supports n-dimensional points in Python3.8
    # only the two dimensional case was supported before Python3.8
    _hypot_for_n_dimension = hypot
else:

    def _hypot_for_n_dimension(*coordinates: float) -> float:  # type: ignore[misc]
        return sqrt(sum(x * x for x in coordinates))


_V = TypeVar("_V", bound="Vector")
_V2 = TypeVar("_V2", bound="Vector2D")
_V3 = TypeVar("_V3", bound="Vector3D")

_T = Union["Vector2D", "Vector3D"]


class Vector(UserSequence[float]):
    """This class defines the basic concept of Vector.

    :class:`Vector` contains the coordinates of a 2D vector or a 3D vector.

    Arguments:
        x: The x coordinate of the vector.
        y: The y coordinate of the vector.
        z: The z coordinate of the vector.

    Examples:
        >>> Vector(1, 2)
        Vector2D(1, 2)

        >>> Vector(1, 2, 3)
        Vector3D(1, 2, 3)

    """

    _data: Tuple[float, ...]

    _repr_type = ReprType.INSTANCE

    _DIMENSION: Optional[int] = None

    def __new__(  # type: ignore[misc]  # pylint: disable=unused-argument
        cls: Type[_V],
        x: float,
        y: float,
        z: Optional[float] = None,
    ) -> _T:
        """Create a new instance of :class:`Vector`.

        Arguments:
            x: The x coordinate of the vector.
            y: The y coordinate of the vector.
            z: The z coordinate of the vector.

        Returns:
            The created :class:`Vector2D` or :class:`Vector3D` object.

        """
        ReturnType = Vector2D if z is None else Vector3D

        obj: _T = object.__new__(ReturnType)
        return obj

    def __bool__(self) -> bool:
        return any(self._data)

    def __neg__(self: _V) -> _V:
        result: _V = object.__new__(self.__class__)
        result._data = tuple(-coordinate for coordinate in self._data)
        return result

    def __add__(self: _V, other: Iterable[float]) -> _V:
        """Calculate the sum of the vector and other vector.

        Arguments:
            other: The added vector.

        Returns:
            The sum vector of adding two vectors.

        """
        try:
            result: _V = object.__new__(self.__class__)
            result._data = tuple(i + j for i, j in zip_longest(self._data, other))
            return result
        except TypeError:
            return NotImplemented

    def __radd__(self: _V, other: Sequence[float]) -> _V:
        """Calculate the sum of the vector and the other vector.

        Arguments:
            other: The added vector.

        Returns:
            The sum vector of adding two vectors.

        """
        return self.__add__(other)

    def __sub__(self: _V, other: Iterable[float]) -> _V:
        try:
            result: _V = object.__new__(self.__class__)
            result._data = tuple(i - j for i, j in zip_longest(self._data, other))
            return result
        except TypeError:
            return NotImplemented

    def __rsub__(self: _V, other: Iterable[float]) -> _V:
        try:
            result: _V = object.__new__(self.__class__)
            result._data = tuple(i - j for i, j in zip_longest(other, self._data))
            return result
        except TypeError:
            return NotImplemented

    def __mul__(self: _V, other: float) -> _V:
        try:
            if isinstance(other, (int, float)):
                result: _V = object.__new__(self.__class__)
                result._data = tuple(i * other for i in self._data)
                return result
        except TypeError:
            pass

        return NotImplemented

    def __rmul__(self: _V, other: float) -> _V:
        return self.__mul__(other)

    def __truediv__(self: _V, other: float) -> _V:
        try:
            if isinstance(other, (int, float)):
                result: _V = object.__new__(self.__class__)
                result._data = tuple(i / other for i in self._data)
                return result
        except TypeError:
            pass

        return NotImplemented

    def __floordiv__(self: _V, other: float) -> _V:
        try:
            if isinstance(other, (int, float)):
                result: _V = object.__new__(self.__class__)
                result._data = tuple(i // other for i in self._data)
                return result
        except TypeError:
            pass

        return NotImplemented

    def __abs__(self) -> float:
        return _hypot_for_n_dimension(*self._data)

    def _repr_head(self) -> str:
        return f"{self.__class__.__name__}{self._data}"

    @staticmethod
    def loads(contents: Dict[str, float]) -> _T:
        """Loads a :class:`Vector` from a dict containing coordinates of the vector.

        Arguments:
            contents: A dict containing coordinates of the vector.

        Returns:
            The loaded :class:`Vector2D` or :class:`Vector3D` object.

        Examples:
            >>> contents = {"x": 1.0, "y": 2.0}
            >>> Vector.loads(contents)
            Vector2D(1.0, 2.0)

            >>> contents = {"x": 1.0, "y": 2.0, "z": 3.0}
            >>> Vector.loads(contents)
            Vector3D(1.0, 2.0, 3.0)

        """
        if "z" in contents:
            return Vector3D.loads(contents)
        return Vector2D.loads(contents)


class Vector2D(Vector):
    """This class defines the concept of Vector2D.

    :class:`Vector2D` contains the coordinates of a 2D vector.

    Arguments:
        x: The x coordinate of the 2D vector.
        y: The y coordinate of the 2D vector.

    Examples:
        >>> Vector2D(1, 2)
        Vector2D(1, 2)

    """

    _DIMENSION = 2

    def __new__(  # pylint: disable=unused-argument
        cls: Type[_V2], *args: float, **kwargs: float
    ) -> _V2:
        """Create a :class:`Vector2D` instance.

        Arguments:
            args: The coordinates of the 2D vector.
            kwargs: The coordinates of the 2D vector.

        Returns:
            The created :class:`Vector2D` instance.

        """
        obj: _V2 = object.__new__(cls)
        return obj

    def __init__(self, x: float, y: float) -> None:
        self._data = (x, y)

    def __abs__(self) -> float:
        return hypot(*self._data)

    @classmethod
    def loads(cls: Type[_V2], contents: Dict[str, float]) -> _V2:
        """Load a :class:`Vector2D` object from a dict containing coordinates of a 2D vector.

        Arguments:
            contents: A dict containing coordinates of a 2D vector.

        Returns:
            The loaded :class:`Vector2D` object.

        Examples:
            >>> contents = {"x": 1.0, "y": 2.0}
            >>> Vector2D.loads(contents)
            Vector2D(1.0, 2.0)

        """
        return cls(**contents)

    @property
    def x(self) -> float:
        """Return the x coordinate of the vector.

        Returns:
            X coordinate in float type.

        Examples:
            >>> vector_2d = Vector2D(1, 2)
            >>> vector_2d.x
            1

        """
        return self._data[0]

    @property
    def y(self) -> float:
        """Return the y coordinate of the vector.

        Returns:
            Y coordinate in float type.

        Examples:
            >>> vector_2d = Vector2D(1, 2)
            >>> vector_2d.y
            2

        """
        return self._data[1]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector into a dict.

        Returns:
            A dict containing the vector coordinate.

        Examples:
                >>> vector_2d = Vector2D(1, 2)
                >>> vector_2d.dumps()
                {'x': 1, 'y': 2}

        """
        return {"x": self._data[0], "y": self._data[1]}


class Vector3D(Vector):
    """This class defines the concept of Vector3D.

    :class:`Vector3D` contains the coordinates of a 3D Vector.

    Arguments:
        x: The x coordinate of the 3D vector.
        y: The y coordinate of the 3D vector.
        z: The z coordinate of the 3D vector.

    Examples:
        >>> Vector3D(1, 2, 3)
        Vector3D(1, 2, 3)

    """

    _DIMENSION = 3

    def __new__(  # pylint: disable=unused-argument
        cls: Type[_V3], *args: float, **kwargs: float
    ) -> _V3:
        """Create a :class:`Vector3D` instance.

        Arguments:
            args: The coordinates of the 3D vector.
            kwargs: The coordinates of the 3D vector.

        Returns:
            The created :class:`Vector3D` instance.

        """
        obj: _V3 = object.__new__(cls)
        return obj

    def __init__(self, x: float, y: float, z: float) -> None:
        self._data = (x, y, z)

    @classmethod
    def loads(cls: Type[_V3], contents: Dict[str, float]) -> _V3:
        """Load a :class:`Vector3D` object from a dict containing coordinates of a 3D vector.

        Arguments:
            contents: A dict contains coordinates of a 3D vector.

        Returns:
            The loaded :class:`Vector3D` object.

        Examples:
            >>> contents = {"x": 1.0, "y": 2.0, "z": 3.0}
            >>> Vector3D.loads(contents)
            Vector3D(1.0, 2.0, 3.0)

        """
        return cls(**contents)

    @property
    def x(self) -> float:
        """Return the x coordinate of the vector.

        Returns:
             X coordinate in float type.

        Examples:
            >>> vector_3d = Vector3D(1, 2, 3)
            >>> vector_3d.x
            1

        """
        return self._data[0]

    @property
    def y(self) -> float:
        """Return the y coordinate of the vector.

        Returns:
            Y coordinate in float type.

        Examples:
            >>> vector_3d = Vector3D(1, 2, 3)
            >>> vector_3d.y
            2

        """
        return self._data[1]

    @property
    def z(self) -> float:
        """Return the z coordinate of the vector.

        Returns:
            Z coordinate in float type.

        Examples:
            >>> vector_3d = Vector3D(1, 2, 3)
            >>> vector_3d.z
            3

        """
        return self._data[2]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector into a dict.

        Returns:
            A dict containing the vector coordinates.

        Examples:
            >>> vector_3d = Vector3D(1, 2, 3)
            >>> vector_3d.dumps()
            {'x': 1, 'y': 2, 'z': 3}

        """
        return {"x": self._data[0], "y": self._data[1], "z": self._data[2]}
