#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""CameraMatrix, DistortionCoefficients and CameraIntrinsics.

:class:`CameraMatrix` represents camera matrix. It describes the mapping of
a pinhole camera model from 3D points in the world to 2D points in an image.

:class:`DistortionCoefficients` represents camera distortion coefficients. It is the deviation
from rectilinear projection including radial distortion and tangential distortion.

:class:`CameraIntrinsics` represents camera intrinsics including camera matrix and
distortion coeffecients. It describes the mapping of the scene in front of the camera
to the pixels in the final image.

:class:`CameraMatrix`, :class:`DistortionCoefficients` and :class:`CameraIntrinsics` class can
all be initialized by :meth:`__init__()` or :meth:`loads()` method.

"""

import math
from itertools import count
from typing import Dict, Iterator, Optional, Sequence, Tuple, Type, TypeVar

import numpy as np

from ..geometry import Vector2D
from ..utility import ReprMixin, ReprType, common_loads


class CameraMatrix(ReprMixin):
    """CameraMatrix represents camera matrix.

    Camera matrix describes the mapping of a pinhole camera model from 3D points in the world
    to 2D points in an image.

    Arguments:
        matrix: A 3x3 Sequence of camera matrix.
        **kwargs: Float values with keys: "fx", "fy", "cx", "cy" and "skew"(optional).

    Attributes:
        fx: The x axis focal length expressed in pixels.
        fy: The y axis focal length expressed in pixels.
        cx: The x coordinate of the so called principal point that should be in the center of
            the image.
        cy: The y coordinate of the so called principal point that should be in the center of
            the image.
        skew: It causes shear distortion in the projected image.

    Raises:
        TypeError: When only keyword arguments with incorrect keys are provided,
            or when no arguments are provided.

    """

    _T = TypeVar("_T", bound="CameraMatrix")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("fx", "fy", "cx", "cy", "skew")

    def __init__(
        self,
        matrix: Optional[Sequence[Sequence[float]]] = None,
        **kwargs: float,
    ) -> None:
        if kwargs:
            try:
                self._loads(kwargs)
                return
            except KeyError as error:
                if matrix is None:
                    raise TypeError(
                        f"Missing key {error} in kwargs to initialize {self.__class__.__name__}"
                    ) from error

        if matrix is not None:
            self.fx = matrix[0][0]  # pylint: disable=invalid-name
            self.fy = matrix[1][1]  # pylint: disable=invalid-name
            self.cx = matrix[0][2]  # pylint: disable=invalid-name
            self.cy = matrix[1][2]  # pylint: disable=invalid-name
            self.skew = matrix[0][1]
            return

        raise TypeError(f"Require 'fx', 'fy', 'cx', 'cy' to initialize {self.__class__.__name__}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return (
            self.fx == other.fx
            and self.fy == other.fy
            and self.cx == other.cx
            and self.cy == other.cy
            and self.skew == other.skew
        )

    def _loads(self, contents: Dict[str, float]) -> None:
        self.fx = contents["fx"]
        self.fy = contents["fy"]
        self.cx = contents["cx"]
        self.cy = contents["cy"]
        self.skew = contents.get("skew", 0)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Loads CameraMatrix from a dict containing the information of the camera matrix.

        Arguments:
            contents: A dict containing the information of the camera matrix.

        Returns:
            A :class:`CameraMatrix` instance contains the information from the contents dict.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, float]:
        """Dumps the camera matrix into a dict.

        Returns:
            A dict containing the information of the camera matrix.

        """
        return {
            "fx": self.fx,
            "fy": self.fy,
            "cx": self.cx,
            "cy": self.cy,
            "skew": self.skew,
        }

    def as_matrix(self) -> np.ndarray:
        """Return the camera matrix as a 3x3 numpy array.

        Returns:
            A 3x3 numpy array representing the camera matrix.

        """
        return np.array(
            [
                [self.fx, self.skew, self.cx],
                [0.0, self.cy, self.cy],
                [0.0, 0.0, 1.0],
            ]
        )

    def project(self, point: Sequence[float]) -> Vector2D:
        """Project a point to the pixel coordinates.

        Arguments:
            point: A Sequence containing the coordinates of the point to be projected.

        Returns:
            The pixel coordinates.

        Raises:
            TypeError: When the dimension of the input point is neither two nor three.

        """
        if len(point) == 3:
            x = point[0] / point[2]
            y = point[1] / point[2]
        elif len(point) == 2:
            x = point[0]
            y = point[1]
        else:
            raise TypeError("The point to be projected must have 2 or 3 dimension")

        x = self.fx * x + self.skew * y + self.cx
        y = self.fy * y + self.cy
        return Vector2D(x, y)


class DistortionCoefficients(ReprMixin):
    """DistortionCoefficients represents camera distortion coefficients.

    Distortion is the deviation from rectilinear projection including radial distortion
    and tangential distortion.

    Arguments:
        **kwargs: Float values with keys: k1, k2, ... and p1, p2, ...

    Raises:
        TypeError: When tangential and radial distortion is not provided to initialize class.

    """

    _T = TypeVar("_T", bound="DistortionCoefficients")

    _repr_type = ReprType.INSTANCE

    _DISTORTION_KEYS = ("p", "k")
    _FISHEYE_MINIMUM_R = 1e-8

    def __init__(self, **kwargs: float) -> None:
        self._loads(kwargs)

        if not hasattr(self, "k1") and not hasattr(self, "p1"):
            raise TypeError(
                f"Require tangential or radial distortion to initialize {self.__class__.__name__}"
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for key in self._DISTORTION_KEYS:
            if tuple(self._list_distortions(key)) != tuple(other._list_distortions(key)):
                return False

        return True

    @staticmethod
    def _distortion_generator(
        distortion_keyword: str, data: Dict[str, float]
    ) -> Iterator[Tuple[str, float]]:
        for index in range(1, len(data) + 1):
            key = f"{distortion_keyword}{index}"
            if key not in data:
                break
            yield (key, data[key])

    @property
    def _repr_attrs(self) -> Iterator[str]:  # type: ignore[override]
        for distortion_key in self._DISTORTION_KEYS:
            for index in count(1):
                distortion_name = f"{distortion_key}{index}"
                if not hasattr(self, distortion_name):
                    break
                yield distortion_name

    def _calculate_radial_distortion(self, r2: float, is_fisheye: bool = False) -> float:
        # pylint: disable=invalid-name
        if is_fisheye:
            r = math.sqrt(r2)
            factor = math.atan(r)
            factor2 = factor ** 2
        else:
            factor2 = r2

        radial_distortion = 1.0
        for i, value in enumerate(self._list_distortions("k"), 1):
            radial_distortion += value * factor2 ** i

        if is_fisheye:
            radial_distortion = radial_distortion * factor / r if r > self._FISHEYE_MINIMUM_R else 1
        return radial_distortion

    def _calculate_tangential_distortion(  # pylint: disable=too-many-arguments
        self, r2: float, x2: float, y2: float, xy2: float, is_fisheye: bool
    ) -> Tuple[float, float]:
        # pylint: disable=invalid-name
        if is_fisheye:
            return (0, 0)

        p1 = self.p1  # type: ignore[attr-defined]  # pylint: disable=no-member
        p2 = self.p2  # type: ignore[attr-defined]  # pylint: disable=no-member
        return (p1 * xy2 + p2 * (r2 + 2 * x2), p1 * (r2 + 2 * y2) + p2 * xy2)

    def _loads(self, contents: Dict[str, float]) -> None:
        for distortion_key in self._DISTORTION_KEYS:
            for key, value in self._distortion_generator(distortion_key, contents):
                setattr(self, key, value)

    def _list_distortions(self, distortion_key: str) -> Iterator[float]:
        """Return the tangential or radial distortion coefficients list.

        Arguments:
            distortion_key: "p" or "k" indicating tangential or radial distortion.

        Yields:
            All the tangential or radial distortion coefficients.

        """
        for index in count(1):
            distortion_value = getattr(self, f"{distortion_key}{index}", None)
            if distortion_value is None:
                break
            yield distortion_value

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Loads DistortionCoefficients from a dict containing the information.

        Arguments:
            contents: A dict containig distortion coefficients of a camera.

        Returns:
            A :class:`DistortionCoefficients` instance containing information from
            the contents dict.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, float]:
        """Dumps the distortion coefficients into a dict.

        Returns:
            A dict containing the information of distortion coefficients.

        """
        contents = {}
        for distortion_key in self._DISTORTION_KEYS:
            distortions = self._list_distortions(distortion_key)
            for index, value in enumerate(distortions, 1):
                contents[f"{distortion_key}{index}"] = value

        return contents

    def distort(self, point: Sequence[float], is_fisheye: bool = False) -> Vector2D:
        """Add distortion to a point.

        Arguments:
            point: A Sequence containing the coordinates of the point to be distorted.
            is_fisheye: Whether the sensor is fisheye camera, default is False.

        Raises:
            TypeError: When the dimension of the input point is neither two nor three.

        Returns:
            Distorted 2d point.

        """
        # pylint: disable=invalid-name
        if len(point) == 3:
            x = point[0] / point[2]
            y = point[1] / point[2]
        elif len(point) == 2:
            x = point[0]
            y = point[1]
        else:
            raise TypeError("The point to be projected must have 2 or 3 dimension")

        x2 = x ** 2
        y2 = y ** 2
        xy2 = 2 * x * y
        r2 = x2 + y2

        radial_distortion = self._calculate_radial_distortion(r2, is_fisheye)
        tangential_distortion = self._calculate_tangential_distortion(r2, x2, y2, xy2, is_fisheye)
        x = x * radial_distortion + tangential_distortion[0]
        y = y * radial_distortion + tangential_distortion[1]
        return Vector2D(x, y)


class CameraIntrinsics(ReprMixin):
    """CameraIntrinsics represents camera intrinsics.

    Camera intrinsic parameters including camera matrix and distortion coeffecients.
    They describe the mapping of the scene in front of the camera to the pixels in the final image.

    Arguments:
        camera_matrix: A 3x3 Sequence of the camera matrix.
        _init_distortion: Whether init distortion, default is True.
        **kwargs: Float values to initialize :class:`CameraMatrix` and
            :class:`DistortionCoefficients`.

    Attributes:
        _camera_matrix: A 3x3 Sequence of the camera matrix.
        _distortion_coefficients: It is the deviation from rectilinear projection. It includes
            radial distortion and tangential distortion.

    """

    _T = TypeVar("_T", bound="CameraIntrinsics")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("camera_matrix", "distortion_coefficients")
    _repr_maxlevel = 2

    def __init__(
        self,
        camera_matrix: Optional[Sequence[Sequence[float]]] = None,
        *,
        _init_distortion: bool = True,
        **kwargs: float,
    ) -> None:
        self._camera_matrix = CameraMatrix(camera_matrix, **kwargs)
        self._distortion_coefficients: Optional[DistortionCoefficients]
        if kwargs and _init_distortion:
            try:
                self._distortion_coefficients = DistortionCoefficients.loads(kwargs)
                return
            except TypeError:
                pass
        self._distortion_coefficients = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return (
            self.camera_matrix == other.camera_matrix
            and self.distortion_coefficients == other.distortion_coefficients
        )

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._camera_matrix = CameraMatrix.loads(contents["cameraMatrix"])
        if "distortionCoefficients" in contents:
            self._distortion_coefficients = DistortionCoefficients.loads(
                contents["distortionCoefficients"]
            )
        else:
            self._distortion_coefficients = None

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Loads CameraIntrinsics from a dict containing the information.

        Arguments:
            contents: A dict containig camera matrix and distortion coefficients.

        Returns:
            A :class:`CameraIntrinsics` instance containing information from
            the contents dict.

        """
        return common_loads(cls, contents)

    @property
    def camera_matrix(self) -> CameraMatrix:
        """Get the camera matrix of the camera intrinsics.

        Returns:
            :class:`CameraMatrix` class object containing fx, fy, cx, cy, skew(optional).

        """
        return self._camera_matrix

    @property
    def distortion_coefficients(self) -> Optional[DistortionCoefficients]:
        """Get the distortion coefficients of the camera intrinsics, could be None.

        Returns:
            :class:`DistortionCoefficients` class object containing tangential and
            radial distortion coefficients.

        """
        return self._distortion_coefficients

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the camera intrinsics into a dict.

        Returns:
            A dict containing camera intrinsics.

        """
        contents = {"cameraMatrix": self._camera_matrix.dumps()}
        if self._distortion_coefficients:
            contents["distortionCoefficients"] = self._distortion_coefficients.dumps()

        return contents

    def set_camera_matrix(
        self,
        matrix: Optional[Sequence[Sequence[float]]] = None,
        **kwargs: float,
    ) -> None:
        """Set camera matrix of the camera intrinsics.

        Arguments:
            matrix: Camera matrix in 3x3 sequence.
            **kwargs: Contains fx, fy, cx, cy, skew(optional)

        """
        self._camera_matrix = CameraMatrix(matrix=matrix, **kwargs)

    def set_distortion_coefficients(self, **kwargs: float) -> None:
        """Set distortion coefficients of the camera intrinsics.

        Arguments:
            **kwargs: Contains p1, p2, ..., k1, k2, ...

        """
        self._distortion_coefficients = DistortionCoefficients(**kwargs)

    def project(self, point: Sequence[float], is_fisheye: bool = False) -> Vector2D:
        """Project a point to the pixel coordinates.

        If distortion coefficients are provided, distort the point before projection.

        Arguments:
            point: A Sequence containing coordinates of the point to be projected.
            is_fisheye: Whether the sensor is fisheye camera, default is False.

        Returns:
            The coordinates on the pixel plane where the point is projected to.

        """
        if self._distortion_coefficients:
            point = self._distortion_coefficients.distort(point, is_fisheye)
        return self._camera_matrix.project(point)
