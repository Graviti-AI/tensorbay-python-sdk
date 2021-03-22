#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Quaternion.

:class:`Quaternion` contains the coordinates of a quaternion and
can be used generically as 4D numbers,
or as unit quaternions to represent rotations in 3D space.

"""

import math
import warnings
from typing import Dict, Optional, Sequence, Type, TypeVar, Union, overload

import numpy as np

from ..utility import common_loads
from .vector import Vector3D

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import quaternion


_T = TypeVar("_T", bound="Quaternion")


class Quaternion:
    """This class defines the concept of Quaternion.

    :class:`Quaternion` contains the coordinates of a quaternion and
    can be used generically as 4D numbers,
    or as unit quaternions to represent rotations in 3D space.

    :class:`Quaternion` can be initialized in the following ways:

        1. Init from w, x, y, z components.

            .. code:: python

                >>> Quaternion(1)
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

                >>> Quaternion(w=1, x=0, y=0, z=0)
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

                >>> Quaternion(1.0, 0.0, 0.0, 0.0)
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

                >>> Quaternion([1.0, 0.0, 0.0, 0.0])
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

        2. Init from a 3*3 or 3*4 or 4*4 sequence/numpy array.

            .. code:: python

                >>> Quaternion([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

        3. Init from None.

            .. code:: python

                >>> Quaternion(None)
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

        4. Init from rotation vector.

            .. code:: python

                >>> Quaternion(rotation_vector=[0, 0, 0])
                >>> Quaternion(1.0, 0.0, 0.0, 0.0)

        5. Init from axis angle.

            .. code:: python

                >>> Quaternion(axis=[1, 0, 0], radians=1.57)
                >>> Quaternion(0.7073882691671998, 0.706825181105366, 0.0, 0.0)

                >>> Quaternion(axis=[1, 0, 0], degrees=90)
                >>> Quaternion(0.7073882691671998, 0.706825181105366, 0.0, 0.0)

        6. Init from spherical coordinate.

            .. code:: python

                >>> Quaternion(spherical_coords=[1.57, 0.0])
                >>> Quaternion(0.7073882691671998, -0.0, 0.706825181105366, 0.0)

        7. Init from euler angle.

            .. code:: python

                >>> Quaternion(euler_angle=[0, 1.57, 0])
                >>> Quaternion(0.7073882691671998, -0.0, 0.706825181105366, 0.0)

    Arguments:
        *args: Coordinates of the :class:`Quaternion`.
        **kwargs: keyword-only argument to the :class:`Quaternion`.

    Raises:
        TypeError: If the shape of the input matrix args is not 3x3 or 3x4 or 4x4.

    """

    ArgsType = Union[
        None,
        Sequence[float],
        Sequence[Sequence[float]],
        np.ndarray,
        quaternion.quaternion,
        "Quaternion",
    ]
    KwargsType = Union[None, float, Sequence[float], np.ndarray]

    def __init__(
        self,
        *args: Union[ArgsType, float],
        **kwargs: KwargsType,
    ) -> None:
        if kwargs:
            self._data: quaternion.quaternion = self._quaternion_from_kwargs(kwargs)
            if self._data:
                return

        arg = args[0] if len(args) == 1 else args
        if isinstance(arg, Sequence) and arg:  # pylint: disable=W1116
            arg = np.array(arg, dtype=np.float64)

        if isinstance(arg, np.ndarray):
            if arg.shape == (3, 3) or arg.shape == (3, 4) or arg.shape == (4, 4):
                self._data = quaternion.from_rotation_matrix(arg[:3, :3])
                return

            if len(arg.shape) > 1:
                raise TypeError(
                    "Only support 3x3, 3x4 and 4x4 matrix input"
                    f"to initialize {self.__class__.__name__}"
                )

            self._data = quaternion.quaternion(*arg)
            return

        if not arg:
            self._data = quaternion.quaternion(1, 0, 0, 0)
            return

        if isinstance(arg, Quaternion):
            self._data = quaternion.quaternion(arg._data)
            return

        self._data = quaternion.quaternion(arg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self._data.w}, "
            f"{self._data.x}, "
            f"{self._data.y}, "
            f"{self._data.z})"
        )

    def __bool__(self) -> bool:
        return self._data.__bool__()  # type: ignore[no-any-return]

    def __neg__(self: _T) -> _T:
        return self._create(self._data.__neg__())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quaternion):
            return False

        return self._data.__eq__(other._data)  # type: ignore[no-any-return]

    def __add__(self: _T, other: object) -> _T:
        if not isinstance(other, Quaternion):
            return NotImplemented

        return self._create(self._data.__add__(other._data))

    def __sub__(self: _T, other: object) -> _T:
        if not isinstance(other, Quaternion):
            return NotImplemented

        return self._create(self._data.__sub__(other._data))

    @overload
    def __mul__(self: _T, other: _T) -> _T:
        ...

    @overload
    def __mul__(self: _T, other: Sequence[float]) -> Vector3D:
        ...

    @overload
    def __mul__(self: _T, other: np.ndarray) -> Vector3D:
        ...

    # mypy errors to be figured out
    # when swapping overload 2 and 3
    # 1) Overloaded function signature 3 will never be matched:
    #    signature 2's parameter type(s) are the same or broader
    # when use Union to describe overload 2 and 3 in one
    # 2) Overloaded function signatures 1 and 2 overlap with incompatible return types

    def __mul__(self: _T, other: Union[_T, np.ndarray, Sequence[float]]) -> Union[_T, Vector3D]:
        if isinstance(other, Quaternion):
            return self._create(self._data.__mul__(other._data))

        if isinstance(other, (Sequence, np.ndarray)):  # pylint: disable=W1116
            return self.rotate(other)

        return NotImplemented

    @staticmethod
    def _quaternion_from_kwargs(kwargs: Dict[str, KwargsType]) -> Optional[quaternion.quaternion]:
        if "rotation_vector" in kwargs:
            return quaternion.from_rotation_vector(kwargs["rotation_vector"])

        if "spherical_coords" in kwargs:
            return quaternion.from_spherical_coords(kwargs["spherical_coords"])

        if "euler_angle" in kwargs:
            return quaternion.from_euler_angles(kwargs["euler_angle"])

        if "axis" in kwargs:
            if "degrees" in kwargs:
                angle = math.radians(kwargs["degrees"])  # type: ignore[arg-type]
            else:
                angle = kwargs["radians"]  # type: ignore[assignment]
            norm = np.linalg.norm(kwargs["axis"])
            return quaternion.from_rotation_vector(
                [x * angle / norm for x in kwargs["axis"]]  # type: ignore[union-attr]
            )

        if "w" in kwargs or "x" in kwargs or "y" in kwargs or "z" in kwargs:
            return Quaternion._quaternion_from_wxyz(kwargs)  # type: ignore[arg-type]

        return None

    @staticmethod
    def _quaternion_from_wxyz(kwargs: Dict[str, float]) -> quaternion.quaternion:
        return quaternion.quaternion(kwargs["w"], kwargs["x"], kwargs["y"], kwargs["z"])

    @classmethod
    def _create(cls: Type[_T], data: quaternion.quaternion) -> _T:
        obj: _T = object.__new__(cls)
        obj._data = data  # pylint: disable=protected-access
        return obj

    def _loads(self, contents: Dict[str, float]) -> None:
        self._data = self._quaternion_from_wxyz(contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a :class:`Quaternion` from a dict.

        Arguments:
            contents: A dict containing coordinates of a :class:`Quaternion`::

                {
                    "w": ...
                    "x": ...
                    "y": ...
                    "z": ...
                }

        Returns:
            The loaded :class:`Quaternion` object.

        """
        return common_loads(cls, contents)

    @property
    def w(self) -> float:
        """Return the w component of the quaternion.

        Returns:
            W component of the quaternion.

        """
        return self._data.w  # type: ignore[no-any-return]

    @property
    def x(self) -> float:
        """Return the x component of the quaternion.

        Returns:
            X component of the quaternion.

        """
        return self._data.x  # type: ignore[no-any-return]

    @property
    def y(self) -> float:
        """Return the y component of the quaternion.

        Returns:
            Y component of the quaternion.

        """
        return self._data.y  # type: ignore[no-any-return]

    @property
    def z(self) -> float:
        """Return the z component of the quaternion.

        Returns:
            Z component of the quaternion.

        """
        return self._data.z  # type: ignore[no-any-return]

    @property
    def radians(self) -> float:
        """Return the angle of the quaternion in radians.

        Returns:
            Angle of the quaternion in radians.

        """
        return self._data.angle()  # type: ignore[no-any-return]

    @property
    def degrees(self) -> float:
        """Return the angle of the quaternion in degrees.

        Returns:
            Angle of the quaternion in degrees.

        """
        return math.degrees(self._data.angle())

    def as_matrix(self) -> np.ndarray:
        """Return the quaternion as a rotation matrix.

        Returns:
            A rotation matrix contains the quaternion.
        """
        return quaternion.as_rotation_matrix(self._data)

    def inverse(self: _T) -> _T:
        """Return the inverse of the quaternion.

        Returns:
            A :class:`Quaternion` object representing the inverse of this :class:`Quaternion`.

        """
        return self._create(self._data.inverse())

    def rotate(self, vector: Union[Sequence[float], np.ndarray]) -> Vector3D:
        """Rotate the input vector using this quaternion.

        Arguments:
            vector: The vector to be rotated.

        Returns:
            Rotated vector.

        """
        rotated_vector = Vector3D(*quaternion.rotate_vectors(self._data, vector))
        return rotated_vector

    def dumps(self) -> Dict[str, float]:
        """Dumps the Quaternion into a dict.

        Returns:
            A dict containing the Quaternion information.

        """
        return {"w": self._data.w, "x": self._data.x, "y": self._data.y, "z": self._data.z}
