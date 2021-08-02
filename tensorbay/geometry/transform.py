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
from typing import Dict, Iterable, Optional, Type, TypeVar, Union, overload

import numpy as np

from ..utility import MatrixType, ReprMixin, ReprType, common_loads
from .vector import Vector3D

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from quaternion import as_rotation_matrix, from_rotation_matrix
    from quaternion import quaternion as Quaternion
    from quaternion import rotate_vectors

_T = TypeVar("_T", bound="Transform3D")


class Transform3D(ReprMixin):
    """This class defines the concept of Transform3D.

    :class:`Transform3D` contains rotation and translation of the 3D transform.

    Arguments:
        translation: Translation in a sequence of [x, y, z].
        rotation: Rotation in a sequence of [w, x, y, z] or numpy quaternion.
        matrix: A 4x4 or 3x4 transform matrix.

    Raises:
        ValueError: If the shape of the input matrix is not correct.

    Examples:
        *Initialization Method 1:* Init from translation and rotation.

        >>> Transform3D([1, 1, 1], [1, 0, 0, 0])
        Transform3D(
          (translation): Vector3D(1, 1, 1),
          (rotation): quaternion(1, 0, 0, 0)
        )

        *Initialization Method 2:* Init from transform matrix in sequence.

        >>> Transform3D(matrix=[[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
        Transform3D(
          (translation): Vector3D(1, 1, 1),
          (rotation): quaternion(1, -0, -0, -0)
        )

        *Initialization Method 3:* Init from transform matrix in numpy array.

        >>> import numpy as np
        >>> Transform3D(matrix=np.array([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]))
        Transform3D(
          (translation): Vector3D(1, 1, 1),
          (rotation): quaternion(1, -0, -0, -0)
        )

    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("translation", "rotation")

    RotationType = Union[Iterable[float], Quaternion]

    def __init__(
        self,
        translation: Iterable[float] = (0, 0, 0),
        rotation: RotationType = (1, 0, 0, 0),
        *,
        matrix: Optional[MatrixType] = None,
    ) -> None:
        if matrix is not None:
            try:
                self._translation = Vector3D(matrix[0][3], matrix[1][3], matrix[2][3])
                self._rotation = from_rotation_matrix(matrix)
                return
            except (IndexError, TypeError) as error:
                raise ValueError(
                    "The shape of input transform matrix must be 3x4 or 4x4."
                ) from error

        self._translation = Vector3D(*translation)
        if isinstance(rotation, Quaternion):
            self._rotation = Quaternion(rotation)
        else:
            self._rotation = Quaternion(*rotation)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._translation.__eq__(other.translation) and self._rotation == other.rotation

    @overload
    def __mul__(self: _T, other: _T) -> _T:
        ...

    @overload
    def __mul__(self, other: Iterable[float]) -> Vector3D:
        ...

    def __mul__(self: _T, other: Union[_T, Iterable[float]]) -> Union[_T, Vector3D]:
        try:
            if isinstance(other, Transform3D):
                return self._create(
                    self._mul_vector(other.translation), self._rotation * other.rotation
                )

            # mypy does not recognize quaternion type, and will infer it as Any.
            # This typing problem to be resolved.
            if isinstance(other, Quaternion):
                return self._create(self._translation, self._rotation * other)

            return self._mul_vector(other)  # type: ignore[arg-type]

        except (TypeError, ValueError):
            pass

        return NotImplemented

    def __rmul__(self: _T, other: Quaternion) -> _T:
        try:
            if isinstance(other, Quaternion):
                return self._create(
                    Vector3D(*rotate_vectors(other, self._translation)),
                    other * self._rotation,
                )
        except ValueError:
            pass

        return NotImplemented

    @classmethod
    def _create(cls: Type[_T], translation: Vector3D, rotation: Quaternion) -> _T:
        transform: _T = object.__new__(cls)
        transform._translation = translation  # pylint: disable=protected-access
        transform._rotation = rotation  # pylint: disable=protected-access
        return transform

    def _mul_vector(self, other: Iterable[float]) -> Vector3D:
        # Multiplication with point list is not supported currently.
        # __radd__ is used to ensure the shape of the input object.
        return self._translation.__radd__(rotate_vectors(self._rotation, other))

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._translation = Vector3D.loads(contents["translation"])
        rotation_contents = contents["rotation"]
        self._rotation = Quaternion(
            rotation_contents["w"],
            rotation_contents["x"],
            rotation_contents["y"],
            rotation_contents["z"],
        )

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Load a :class:`Transform3D` from a dict containing rotation and translation.

        Arguments:
            contents: A dict containing rotation and translation of a 3D transform.

        Returns:
            The loaded :class:`Transform3D` object.

        Example:
            >>> contents = {
            ...     "translation": {"x": 1.0, "y": 2.0, "z": 3.0},
            ...     "rotation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
            ... }
            >>> Transform3D.loads(contents)
            Transform3D(
              (translation): Vector3D(1.0, 2.0, 3.0),
              (rotation): quaternion(1, 0, 0, 0)
            )

        """
        return common_loads(cls, contents)

    @property
    def translation(self) -> Vector3D:
        """Return the translation of the 3D transform.

        Returns:
            Translation in :class:`~tensorbay.geometry.vector.Vector3D`.

        Examples:
            >>> transform = Transform3D(matrix=[[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
            >>> transform.translation
            Vector3D(1, 1, 1)

        """
        return self._translation

    @property
    def rotation(self) -> Quaternion:
        """Return the rotation of the 3D transform.

        Returns:
            Rotation in numpy quaternion.

        Examples:
            >>> transform = Transform3D(matrix=[[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
            >>> transform.rotation
            quaternion(1, -0, -0, -0)

        """
        return self._rotation

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the :class:`Transform3D` into a dict.

        Returns:
            A dict containing rotation and translation information
            of the :class:`Transform3D`.

        Examples:
            >>> transform = Transform3D(matrix=[[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
            >>> transform.dumps()
            {
                'translation': {'x': 1, 'y': 1, 'z': 1},
                'rotation': {'w': 1.0, 'x': -0.0, 'y': -0.0, 'z': -0.0},
            }

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

        Examples:
            >>> transform = Transform3D([1, 1, 1], [1, 0, 0, 0])
            >>> transform.set_translation(3, 4, 5)
            >>> transform
            Transform3D(
              (translation): Vector3D(3, 4, 5),
              (rotation): quaternion(1, 0, 0, 0)
            )

        """
        self._translation = Vector3D(x, y, z)

    def set_rotation(
        self,
        w: Optional[float] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        *,
        quaternion: Optional[Quaternion] = None,
    ) -> None:
        """Set the rotation of the transform.

        Arguments:
            w: The w componet of the roation quaternion.
            x: The x componet of the roation quaternion.
            y: The y componet of the roation quaternion.
            z: The z componet of the roation quaternion.
            quaternion: Numpy quaternion representing the rotation.

        Examples:
            >>> transform = Transform3D([1, 1, 1], [1, 0, 0, 0])
            >>> transform.set_rotation(0, 1, 0, 0)
            >>> transform
            Transform3D(
              (translation): Vector3D(1, 1, 1),
              (rotation): quaternion(0, 1, 0, 0)
            )

        """
        if quaternion:
            self._rotation = Quaternion(quaternion)
            return
        self._rotation = Quaternion(w, x, y, z)

    def as_matrix(self) -> np.ndarray:
        """Return the transform as a 4x4 transform matrix.

        Returns:
            A 4x4 numpy array represents the transform matrix.

        Examples:
            >>> transform = Transform3D([1, 2, 3], [0, 1, 0, 0])
            >>> transform.as_matrix()
            array([[ 1.,  0.,  0.,  1.],
                   [ 0., -1.,  0.,  2.],
                   [ 0.,  0., -1.,  3.],
                   [ 0.,  0.,  0.,  1.]])

        """
        matrix: np.ndarray = np.eye(4)
        matrix[:3, 3] = self._translation
        matrix[:3, :3] = as_rotation_matrix(self._rotation)
        return matrix

    def inverse(self: _T) -> _T:
        """Return the inverse of the transform.

        Returns:
            A :class:`Transform3D` object representing the inverse of this :class:`Transform3D`.

        Examples:
            >>> transform = Transform3D([1, 2, 3], [0, 1, 0, 0])
            >>> transform.inverse()
            Transform3D(
              (translation): Vector3D(-1.0, 2.0, 3.0),
              (rotation): quaternion(0, -1, -0, -0)
            )

        """
        rotation = self._rotation.inverse()
        translation = Vector3D(*rotate_vectors(rotation, -self._translation))
        return self._create(translation, rotation)
