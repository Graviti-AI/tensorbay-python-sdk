#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Transform3D.

:class:`Transform3D` contains the rotation and translation of a 3D transform.
:attr:`Transform3D.translation` is stored as :class:`.Vector3D`,
and :attr:`Transform3D.rotation` is stored as `numpy quaternion`_.

.. _numpy quaternion: https://github.com/moble/quaternion/

"""

import warnings
from typing import Dict, Iterable, Sequence, Type, TypeVar, Union, overload

import numpy as np

from ..utility import ReprMixin, ReprType, common_loads
from .vector import Vector3D

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from quaternion import as_rotation_matrix, from_rotation_matrix, quaternion, rotate_vectors

_T = TypeVar("_T", bound="Transform3D")


class Transform3D(ReprMixin):
    """This class defines the concept of Transform3D.

    :class:`Transform3D` contains rotation and translation of the 3D transform.

    Arguments:
        transform: A :class:`Transform3D` or a 4x4 or 3x4 transform matrix.
        translation: Translation in a sequence of [x, y, z].
        rotation: Rotation in a sequence of [w, x, y, z] or numpy quaternion.

    Raises:
        ValueError: If the shape of the input matrix is not correct.

    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("translation", "rotation")

    MatrixType = Union[None, Sequence[Sequence[float]], np.ndarray]
    TransformType = Union[None, "Transform3D", Sequence[Sequence[float]], np.ndarray]
    RotationType = Union[Iterable[float], quaternion]

    def __init__(
        self,
        transform: TransformType = None,
        *,
        translation: Iterable[float] = (0, 0, 0),
        rotation: RotationType = (1, 0, 0, 0),
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
            self._rotation = from_rotation_matrix(transform)
            return

        self._translation = Vector3D(*translation)
        if isinstance(rotation, quaternion):
            self._rotation = quaternion(rotation)
        else:
            self._rotation = quaternion(*rotation)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._translation.__eq__(other.translation) and self._rotation == other.rotation

    @overload
    def __mul__(self: _T, other: _T) -> _T:
        ...

    @overload
    def __mul__(self: _T, other: Sequence[float]) -> Vector3D:
        ...

    def __mul__(self: _T, other: Union[_T, Sequence[float]]) -> Union[_T, Vector3D]:
        if isinstance(other, Sequence):  # pylint: disable=W1116
            result: Vector3D = self._translation + rotate_vectors(self._rotation, other)
            return result

        # mypy does not recognize quaternion type, and will infer it as Any.
        # This typing problem to be resolved.
        if isinstance(other, quaternion):
            return self._create(self._translation, self._rotation * other)

        if isinstance(other, Transform3D):
            return self._create(self * other.translation, self._rotation * other.rotation)

        return NotImplemented  # type: ignore[unreachable]

    def __rmul__(self: _T, other: quaternion) -> _T:
        if isinstance(other, quaternion):
            return self._create(
                Vector3D(*rotate_vectors(other, self._translation)),
                other * self._rotation,
            )

        return NotImplemented

    @classmethod
    def _create(cls: Type[_T], translation: Vector3D, rotation: quaternion) -> _T:
        transform: _T = object.__new__(cls)
        transform._translation = translation  # pylint: disable=protected-access
        transform._rotation = rotation  # pylint: disable=protected-access
        return transform

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._translation = Vector3D.loads(contents["translation"])
        rotation_contents = contents["rotation"]
        self._rotation = quaternion(
            rotation_contents["w"],
            rotation_contents["x"],
            rotation_contents["y"],
            rotation_contents["z"],
        )

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

    @property
    def translation(self) -> Vector3D:
        """Return the translation of the 3D transform.

        Returns:
            Translation in :class:`~tensorbay.geometry.vector.Vector3D`.

        """
        return self._translation

    @property
    def rotation(self) -> quaternion:
        """Return the rotation of the 3D transform.

        Returns:
            Rotation in numpy quaternion.

        """
        return self._rotation

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the :class:`Transform3D` into a dict.

        Returns:
            A dict containing rotation and translation information
                of the :class:`Transform3D`.

        """
        return {
            "translation": self._translation.dumps(),
            "rotation": {
                "w": self._rotation.w,
                "x": self._rotation.x,
                "y": self._rotation.y,
                "z": self._rotation.z,
            },
        }

    def set_translation(self, x: float, y: float, z: float) -> None:
        """Set the translation of the transform.

        Arguments:
            x: The x coordinate of the translation.
            y: The y coordinate of the translation.
            z: The z coordinate of the translation.
                .. code:: python

                    transform.set_translation(x=1, y=2, z=3)

        """
        self._translation = Vector3D(x, y, z)

    def set_rotation(self, rotation: RotationType) -> None:
        """Set the rotation of the transform.

        Arguments:
            rotation: Rotation in a sequence of [w, x, y, z] or numpy quaternion.

        """
        if isinstance(rotation, quaternion):
            self._rotation = quaternion(rotation)
        else:
            self._rotation = quaternion(*rotation)

    def as_matrix(self) -> np.ndarray:
        """Return the transform as a 4x4 transform matrix.

        Returns:
            A 4x4 numpy array represents the transform matrix.

        """
        matrix: np.ndarray = np.eye(4)
        matrix[:3, 3] = self._translation
        matrix[:3, :3] = as_rotation_matrix(self._rotation)
        return matrix

    def inverse(self: _T) -> _T:
        """Return the inverse of the transform.

        Returns:
            A :class:`Transform3D` object representing the inverse of this :class:`Transform3D`.

        """
        rotation = self._rotation.inverse()
        translation = Vector3D(*rotate_vectors(rotation, -self._translation))
        return self._create(translation, rotation)
