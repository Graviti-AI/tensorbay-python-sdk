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

from typing import Dict, Iterable, Optional, Sequence, Tuple, Type, TypeVar, Union

from ..utility import ReprType, UserSequence, common_loads

_T = TypeVar("_T", bound="Vector")


class Vector(UserSequence[float]):
    """This class defines the basic concept of Vector.

    :class:`Vector` contains the coordinates of a 2D vector or a 3D vector.

    Arguments:
        *args: Coordinates of the vector.
        **kwargs: Float coordinates of the vector:

            .. code:: python

                vector2d = Vector(x=1, y=2)
                vector3d = Vector(x=1, y=2, z=3)

    Raises:
        ValueError: If the dimension of the input parameters is not correct.


    """

    _DIMENSION: Optional[int] = None

    _data: Tuple[float, ...]
    _repr_type = ReprType.INSTANCE

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
        """Create a new instance of :class:`Vector`.

        Arguments:
            *args: Coordinates of the vector.
            **kwargs: Float coordinates of the vector::

                .. code:: python

                    vector2d = Vector(x=1, y=2)
                    vector3d = Vector(x=1, y=2, z=3)

        Raises:
            ValueError: If the dimension of the input parameters is not correct.

        Returns:
            The created :class:`Vector2D` or :class:`Vector3D` object.

        """
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
        """Loads a :class:`Vector` from a dict containing coordinates of the vector.

        Arguments:
            contents: A dict containing coordinates of the vector::

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

        Returns:
            The loaded :class:`Vector2D` or :class:`Vector3D` object.

        """
        if "z" in contents:
            return Vector3D.loads(contents)  # type: ignore[return-value]
        return Vector2D.loads(contents)  # type: ignore[return-value]

    def _repr_head(self) -> str:
        return f"{self.__class__.__name__}{self._data}"

    def __add__(self, other: Sequence[float]) -> _T:
        """Calculate the sum of the vector and other vector.

        Arguments:
            other: The added vector.

        Returns:
            The sum vector of adding two vectors.

        Raises:
            ValueError: If the vector to be added has different dimension.

        """
        if not isinstance(other, Sequence):  # pylint: disable=W1116
            return NotImplemented

        if len(self._data) != len(other):
            raise ValueError("Vectors to be added must have the same dimension")
        result: _T = object.__new__(self.__class__)
        result._data = tuple(i + j for i, j in zip(self._data, other))
        return result

    def __radd__(self, other: Sequence[float]) -> _T:
        """Calculate the sum of the vector and the other vector.

        Arguments:
            other: The added vector.

        Returns:
            The sum vector of adding two vectors.

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
    """This class defines the concept of Vector2D.

    :class:`Vector2D` contains the coordinates of a 2D vector.

    Arguments:
        *args: Coordinates of the 2D vector.
        **kwargs: Float x coordinate and y coordinate of the 2D vector.

    Raises:
        TypeError: If the dimension of the input parameters is not correct.

    """

    _DIMENSION = 2

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
        """Create a new instance of :class:`Vector2D`.

        Arguments:
            *args: Coordinates of the 2D vector.
            **kwargs: Float x coordinate and y coordinate of the 2D vector.

        Raises:
            TypeError: If the dimension of the input parameters is not correct.

        Returns:
            The created :class:`Vector2D` object.

        """
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
        """Load a :class:`Vector2D` object from a dict containing coordinates of a 2D vector.

        Arguments:
            contents: A dict containing coordinates of a 2D vector::

                {
                    "x": ...
                    "y": ...
                }

        Returns:
            The loaded :class:`Vector2D` object.

        """
        return common_loads(cls, contents)

    @property
    def x(self) -> float:
        """Return the x coordinate of the vector.

        Returns:
            X coordinate in float type.

        """
        return self._data[0]

    @property
    def y(self) -> float:
        """Return the y coordinate of the vector.

        Returns:
            Y coordinate in float type.

        """
        return self._data[1]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector into a dict.

        Returns:
            A dict containing the vector coordinate.

        """
        return {"x": self._data[0], "y": self._data[1]}


class Vector3D(Vector):
    """This class defines the concept of Vector3D.

    :class:`Vector3D` contains the coordinates of a 3D Vector.

    Arguments:
        *args: Coordinates of the 3D vector.
        **kwargs: Float x coordinate, y coordinate and z coordinate of the 3D vector.

    Raises:
        TypeError: If the dimension of the input parameters is not correct.

    """

    _DIMENSION = 3

    def __new__(
        cls: Type[_T],
        *args: Union[None, float, Iterable[float]],
        **kwargs: float,
    ) -> _T:
        """Create a new instance of :class:`Vector3D`.

        Arguments:
            *args: Coordinates of the 3D vector.
            **kwargs: Float x coordinate, y coordinate and z coordinate of the 3D vector.

        Raises:
            TypeError: If the dimension of the input parameters is not correct.

        Returns:
            The created :class:`Vector3D` object.

        """
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
        """Load a :class:`Vector3D` object from a dict containing coordinates of a 3D vector.

        Arguments:
            contents: A dict contains coordinates of a 3D vector::

                {
                    "x": ...
                    "y": ...
                    "z": ...
                }

        Returns:
            The loaded :class:`Vector3D` object.

        """
        return common_loads(cls, contents)

    def _loads(self: _T, contents: Dict[str, float]) -> None:
        self._data = (contents["x"], contents["y"], contents["z"])

    @property
    def x(self) -> float:
        """Return the x coordinate of the vector.

        Returns:
             X coordinate in float type.

        """
        return self._data[0]

    @property
    def y(self) -> float:
        """Return the y coordinate of the vector.

        Returns:
            Y coordinate in float type.

        """
        return self._data[1]

    @property
    def z(self) -> float:
        """Return the z coordinate of the vector.

        Returns:
            Z coordinate in float type.

        """
        return self._data[2]

    def dumps(self) -> Dict[str, float]:
        """Dumps the vector into a dict.

        Returns:
            A dict containing the vector coordinates.

        """
        return {"x": self._data[0], "y": self._data[1], "z": self._data[2]}
