#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Transform3D.

:class:`Transform3D` contains the rotation and translation of a 3D transform.

"""

from typing import Dict, Iterable, Optional, Sequence, Type, TypeVar, Union, overload

import numpy as np

from ..utility import ReprMixin, ReprType, common_loads
from .quaternion import Quaternion
from .vector import Vector3D

_T = TypeVar("_T", bound="Transform3D")


class Transform3D(ReprMixin):
    """This class defines the concept of Transform3D.

    :class:`Transform3D` contains rotation and translation of the 3D transform.

    Arguments:
        transform: A :class:`Transform3D` or a 4x4 or 3x4 transform matrix.
        translation: Translation in a sequence of [x, y, z].
        rotation: Rotation in a sequence of [w, x, y, z] or a
            3x3 rotation matrix or :class:`~tensorbay.geometry.quaternion.Quaternion`.
        **kwargs: Other parameters to initialize rotation of the transform.
            See :class:`~tensorbay.geometry.quaternion.Quaternion` documents for details.

    Raises:
        ValueError: If the shape of the input matrix is not correct.

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
        """Load a :class:`Transform3D` from a dict containing rotation and translation.

        Arguments:
            contents: A dict containing rotation and translation of a 3D transform::

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

        Returns:
            The loaded :class:`Transform3D` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._translation = Vector3D.loads(contents["translation"])
        self._rotation = Quaternion.loads(contents["rotation"])

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the :class:`Transform3D` into a dict.

        Returns:
            A dict containing rotation and translation information
                of the :class:`Transform3D`.

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
        """Return the translation of the 3D transform.

        Returns:
            Translation in :class:`~tensorbay.geometry.vector.Vector3D`.

        """
        return self._translation

    def set_translation(self, *args: Union[float, Iterable[float]], **kwargs: float) -> None:
        """Set the translation of the transform.

        Arguments:
            *args: Coordinates of the translation vector.
            **kwargs: Keyword-only argument to set different dimension for translation vector:

                .. code:: python

                    transform.set_translation(x=1, y=2, z=3)

        """
        self._translation = Vector3D(*args, **kwargs)

    @property
    def rotation(self) -> Quaternion:
        """Return the rotation of the 3D transform.

        Returns:
            Rotation in :class:`~tensorbay.geometry.quaternion.Quaternion`.

        """
        return self._rotation

    def set_rotation(
        self,
        *args: Union[Quaternion.ArgsType, float],
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        """Set the rotation of the transform.

        Arguments:
            *args: Coordinates of the :class:`Quaternion`.
            **kwargs: Keyword-only argument to the :class:`Quaternion`.

        """
        self._rotation = Quaternion(*args, **kwargs)

    def as_matrix(self) -> np.ndarray:
        """Return the transform as a 4x4 transform matrix.

        Returns:
            A 4x4 numpy array represents the transform matrix.

        """
        matrix = np.eye(4)
        matrix[:3, 3] = self._translation
        matrix[:3, :3] = self._rotation.as_matrix()
        return matrix

    def inverse(self: _T) -> _T:
        """Return the inverse of the transform.

        Returns:
            A :class:`Transform3D` object representing the inverse of this :class:`Transform3D`.

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
