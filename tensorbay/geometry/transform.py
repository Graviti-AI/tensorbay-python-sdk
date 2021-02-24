#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class Transform3D.
"""

from typing import Dict, Iterable, Optional, Sequence, Type, TypeVar, Union, overload

import numpy as np

from ..utility import ReprMixin, ReprType, common_loads
from .quaternion import Quaternion
from .vector import Vector3D

_T = TypeVar("_T", bound="Transform3D")


class Transform3D(ReprMixin):
    """A class used to represent a transformation in 3D.

    :param transform: A Transform3D object or a 4x4 or 3x4 transfrom matrix
    :param translation: Translation in a sequence of [x, y, z]
    :param rotation: Rotation in a sequence of [w, x, y, z] or 3x3 rotation matrix or Quaternion
    :param kwargs: Other parameters to initialize rotation of the transform
    :raises ValueError: When the shape of the input matrix is wrong
    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("translation", "rotation")

    MatrixType = Union[None, Sequence[Sequence[float]], np.ndarray]
    TransformType = Union[None, "Transform3D", Sequence[Sequence[float]], np.ndarray]

    def __init__(
        self,
        transform: TransformType = None,
        *,
        translation: Optional[Iterable[float]] = None,
        rotation: Quaternion.ArgsType = None,
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        if transform is not None:
            if isinstance(transform, Transform3D):
                self._translation = transform.translation
                self._rotation = transform.rotation
                return

            if isinstance(transform, Sequence):  # pylint: disable=W1116
                transform = np.array(transform)
            if transform.shape != (3, 4) and transform.shape != (4, 4):
                raise ValueError("The shape of input transform matrix must be 3x4 or 4x4.")

            self._translation = Vector3D(transform[0, 3], transform[1, 3], transform[2, 3])
            self._rotation = Quaternion(transform)
            return

        self._translation = Vector3D(translation)
        self._rotation = Quaternion(rotation, **kwargs)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Load a Transform3D from a dict containing rotation and translation of the 3D transform.

        :param contents: A dicitionary containing rotation and translation of a 3D transform
        {
            "translation": {
                "x": ...
                "y": ...
                "z": ...
            },
            "rotation": {
                "w": ...
                "x": ...
                "y": ...
                "z": ...
            }
        }
        :return: The loaded Transform3D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._translation = Vector3D.loads(contents["translation"])
        self._rotation = Quaternion.loads(contents["rotation"])

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the 3D transform as a dictionary.

        :return: A dictionary containing rotation and translation information of the transform3D
        """
        return {
            "translation": self._translation.dumps(),
            "rotation": self._rotation.dumps(),
        }

    @overload
    def __mul__(self: _T, other: _T) -> _T:
        ...

    @overload
    def __mul__(self: _T, other: Quaternion) -> _T:
        ...

    @overload
    def __mul__(self: _T, other: Sequence[float]) -> Vector3D:
        ...

    def __mul__(self: _T, other: Union[_T, Quaternion, Sequence[float]]) -> Union[_T, Vector3D]:

        if isinstance(other, Sequence):  # pylint: disable=W1116
            return self._translation + self._rotation.rotate(other)

        if isinstance(other, Quaternion):
            return self._create(self._translation, self._rotation * other)

        if isinstance(other, Transform3D):
            return self._create(self * other.translation, self._rotation * other.rotation)

        return NotImplemented  # type: ignore[unreachable]

    def __rmul__(self: _T, other: Quaternion) -> _T:
        if isinstance(other, Quaternion):
            return self._create(other * self._translation, other * self._rotation)

        return NotImplemented  # type: ignore[unreachable]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._translation.__eq__(other.translation) and self._rotation == other.rotation

        return False

    @property
    def translation(self) -> Vector3D:
        """Returns translation of the 3D transform.

        :return: Translation in Vector3D
        """
        return self._translation

    def set_translation(self, *args: Union[float, Iterable[float]], **kwargs: float) -> None:
        """Set the translation of the transform.

        :param args: Coordinates of the translation vector
        :param kwargs: keyword-only argument to set different dimension for translation vector
            transform.set_translation(x=1, y=2, z=3)
        """
        self._translation = Vector3D(*args, **kwargs)

    @property
    def rotation(self) -> Quaternion:
        """Returns rotation of the 3D transform.

        :return: rotation in Quaternion
        """
        return self._rotation

    def set_rotation(
        self,
        *args: Union[Quaternion.ArgsType, float],
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        """Set the rotation of the transform.

        :param args: Coordinates of the Quaternion
        :param kwargs: keyword-only argument to the Quaternion
        """
        self._rotation = Quaternion(*args, **kwargs)

    def as_matrix(self) -> np.ndarray:
        """Return the transform as a 4x4 transform matrix.

        :return: A 4x4 numpy array representing the transform matrix
        """
        matrix = np.eye(4)
        matrix[:3, 3] = self._translation
        matrix[:3, :3] = self._rotation.as_matrix()
        return matrix

    def inverse(self: _T) -> _T:
        """Return the inverse of the transform.

        :return: A Transform3D object representing the inverse of this Transform3D
        """
        rotation = self._rotation.inverse()
        translation = rotation.rotate(-self._translation)
        return self._create(translation, rotation)

    @classmethod
    def _create(cls: Type[_T], translation: Vector3D, rotation: Quaternion) -> _T:
        transform: _T = object.__new__(cls)
        transform._translation = translation  # pylint: disable=protected-access
        transform._rotation = rotation  # pylint: disable=protected-access
        return transform
