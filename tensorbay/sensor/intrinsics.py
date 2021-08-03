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
from ..utility import AttrsMixin, MatrixType, ReprMixin, ReprType, attr, camel, common_loads


class CameraMatrix(ReprMixin, AttrsMixin):
    """CameraMatrix represents camera matrix.

    Camera matrix describes the mapping of a pinhole camera model from 3D points in the world
    to 2D points in an image.

    Arguments:
        fx: The x axis focal length expressed in pixels.
        fy: The y axis focal length expressed in pixels.
        cx: The x coordinate of the so called principal point that should be in the center of
            the image.
        cy: The y coordinate of the so called principal point that should be in the center of
            the image.
        skew: It causes shear distortion in the projected image.
        matrix: A 3x3 Sequence of camera matrix.

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

    Examples:
        >>> matrix = [[1, 3, 3],
        ...           [0, 2, 4],
        ...           [0, 0, 1]]

        *Initialazation Method 1*: Init from 3x3 sequence array.

        >>> camera_matrix = CameraMatrix(matrix=matrix)
        >>> camera_matrix
        CameraMatrix(
            (fx): 1,
            (fy): 2,
            (cx): 3,
            (cy): 4,
            (skew): 3
        )

        *Initialazation Method 2*: Init from camera calibration parameters, skew is optional.

        >>> camera_matrix = CameraMatrix(fx=1, fy=2, cx=3, cy=4, skew=3)
        >>> camera_matrix
        CameraMatrix(
            (fx): 1,
            (fy): 2,
            (cx): 3,
            (cy): 4,
            (skew): 3
        )



    """

    _T = TypeVar("_T", bound="CameraMatrix")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("fx", "fy", "cx", "cy", "skew")

    fx: float = attr()
    fy: float = attr()
    cx: float = attr()
    cy: float = attr()
    skew: float = attr(default=0)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        fx: Optional[float] = None,
        fy: Optional[float] = None,
        cx: Optional[float] = None,
        cy: Optional[float] = None,
        skew: float = 0,
        *,
        matrix: Optional[MatrixType] = None,
    ) -> None:
        if matrix is not None:
            # pylint: disable=invalid-name
            self.fx: float = matrix[0][0]
            self.fy: float = matrix[1][1]
            self.cx: float = matrix[0][2]
            self.cy: float = matrix[1][2]
            self.skew: float = matrix[0][1]
            return

        if not (fx is None or fy is None or cx is None or cy is None):
            self.fx = fx
            self.fy = fy
            self.cx = cx
            self.cy = cy
            self.skew = skew
            return

        raise TypeError(
            f"Require 'fx', 'fy', 'cx', 'cy' or 3x3 matrix to initialize {self.__class__.__name__}"
        )

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Loads CameraMatrix from a dict containing the information of the camera matrix.

        Arguments:
            contents: A dict containing the information of the camera matrix.

        Returns:
            A :class:`CameraMatrix` instance contains the information from the contents dict.

        Examples:
            >>> contents = {
            ...     "fx": 2,
            ...     "fy": 6,
            ...     "cx": 4,
            ...     "cy": 7,
            ...     "skew": 3
            ... }
            >>> camera_matrix = CameraMatrix.loads(contents)
            >>> camera_matrix
            CameraMatrix(
                (fx): 2,
                (fy): 6,
                (cx): 4,
                (cy): 7,
                (skew): 3
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, float]:
        """Dumps the camera matrix into a dict.

        Returns:
            A dict containing the information of the camera matrix.

        Examples:
            >>> camera_matrix.dumps()
            {'fx': 1, 'fy': 2, 'cx': 3, 'cy': 4, 'skew': 3}

        """
        return self._dumps()

    def as_matrix(self) -> np.ndarray:
        """Return the camera matrix as a 3x3 numpy array.

        Returns:
            A 3x3 numpy array representing the camera matrix.

        Examples:
            >>> numpy_array = camera_matrix.as_matrix()
            >>> numpy_array
            array([[1., 3., 3.],
                   [0., 4., 4.],
                   [0., 0., 1.]])

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

        Examples:
            Project a point in 2 dimensions

            >>> camera_matrix.project([1, 2])
            Vector2D(12, 19)

            Project a point in 3 dimensions

            >>> camera_matrix.project([1, 2, 4])
            Vector2D(6.0, 10.0)

        """
        if len(point) == 3:
            x = point[0] / point[2]
            y = point[1] / point[2]
        elif len(point) == 2:
            x = point[0]
            y = point[1]
        else:
            raise TypeError("The point to be projected must have 2 or 3 dimensions")

        x = self.fx * x + self.skew * y + self.cx
        y = self.fy * y + self.cy
        return Vector2D(x, y)


class DistortionCoefficients(ReprMixin, AttrsMixin):
    """DistortionCoefficients represents camera distortion coefficients.

    Distortion is the deviation from rectilinear projection including radial distortion
    and tangential distortion.

    Arguments:
        **kwargs: Float values with keys: k1, k2, ... and p1, p2, ...

    Raises:
        TypeError: When tangential and radial distortion is not provided to initialize class.

    Examples:
        >>> distortion_coefficients = DistortionCoefficients(p1=1, p2=2, k1=3, k2=4)
        >>> distortion_coefficients
        DistortionCoefficients(
            (p1): 1,
            (p2): 2,
            (k1): 3,
            (k2): 4
        )

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

        p1: float = self.p1  # type: ignore[attr-defined]  # pylint: disable=no-member
        p2: float = self.p2  # type: ignore[attr-defined]  # pylint: disable=no-member
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

        Examples:
            >>> contents = {
            ...     "p1": 1,
            ...     "p2": 2,
            ...     "k1": 3,
            ...     "k2": 4
            ... }
            >>> distortion_coefficients = DistortionCoefficients.loads(contents)
            >>> distortion_coefficients
            DistortionCoefficients(
                (p1): 1,
                (p2): 2,
                (k1): 3,
                (k2): 4
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, float]:
        """Dumps the distortion coefficients into a dict.

        Returns:
            A dict containing the information of distortion coefficients.

        Examples:
            >>> distortion_coefficients.dumps()
            {'p1': 1, 'p2': 2, 'k1': 3, 'k2': 4}

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

        Examples:
            Distort a point with 2 dimensions

            >>> distortion_coefficients.distort((1.0, 2.0))
            Vector2D(134.0, 253.0)

            Distort a point with 3 dimensions

            >>> distortion_coefficients.distort((1.0, 2.0, 3.0))
            Vector2D(3.3004115226337447, 4.934156378600823)

            Distort a point with 2 dimensions, fisheye is True

            >>> distortion_coefficients.distort((1.0, 2.0), is_fisheye=True)
            Vector2D(6.158401093771876, 12.316802187543752)

        """
        # pylint: disable=invalid-name
        if len(point) == 3:
            x = point[0] / point[2]
            y = point[1] / point[2]
        elif len(point) == 2:
            x = point[0]
            y = point[1]
        else:
            raise TypeError("The point to be projected must have 2 or 3 dimensions")

        x2 = x ** 2
        y2 = y ** 2
        xy2 = 2 * x * y
        r2 = x2 + y2

        radial_distortion = self._calculate_radial_distortion(r2, is_fisheye)
        tangential_distortion = self._calculate_tangential_distortion(r2, x2, y2, xy2, is_fisheye)
        x = x * radial_distortion + tangential_distortion[0]
        y = y * radial_distortion + tangential_distortion[1]
        return Vector2D(x, y)


class CameraIntrinsics(ReprMixin, AttrsMixin):
    """CameraIntrinsics represents camera intrinsics.

    Camera intrinsic parameters including camera matrix and distortion coeffecients.
    They describe the mapping of the scene in front of the camera to the pixels in the final image.

    Arguments:
        fx: The x axis focal length expressed in pixels.
        fy: The y axis focal length expressed in pixels.
        cx: The x coordinate of the so called principal point that should be in the center of
            the image.
        cy: The y coordinate of the so called principal point that should be in the center of
            the image.
        skew: It causes shear distortion in the projected image.
        camera_matrix: A 3x3 Sequence of the camera matrix.
        **kwargs: Float values to initialize :class:`DistortionCoefficients`.

    Attributes:
        camera_matrix: A 3x3 Sequence of the camera matrix.
        distortion_coefficients: It is the deviation from rectilinear projection. It includes
        radial distortion and tangential distortion.

    Examples:
        >>> matrix = [[1, 3, 3],
        ...           [0, 2, 4],
        ...           [0, 0, 1]]

        *Initialization Method 1*: Init from 3x3 sequence array.

        >>> camera_intrinsics = CameraIntrinsics(camera_matrix=matrix, p1=5, k1=6)
        >>> camera_intrinsics
        CameraIntrinsics(
            (camera_matrix): CameraMatrix(
                    (fx): 1,
                    (fy): 2,
                    (cx): 3,
                    (cy): 4,
                    (skew): 3
                ),
            (distortion_coefficients): DistortionCoefficients(
                    (p1): 5,
                    (k1): 6
                )
        )

        *Initialization Method 2*: Init from camera calibration parameters, skew is optional.

        >>> camera_intrinsics = CameraIntrinsics(
        ...     fx=1,
        ...     fy=2,
        ...     cx=3,
        ...     cy=4,
        ...     p1=5,
        ...     k1=6,
        ...     skew=3
        ... )
        >>> camera_intrinsics
        CameraIntrinsics(
            (camera_matrix): CameraMatrix(
                (fx): 1,
                (fy): 2,
                (cx): 3,
                (cy): 4,
                (skew): 3
            ),
            (distortion_coefficients): DistortionCoefficients(
                (p1): 5,
                (k1): 6
            )
        )

    """

    _T = TypeVar("_T", bound="CameraIntrinsics")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("camera_matrix", "distortion_coefficients")
    _repr_maxlevel = 2

    camera_matrix: CameraMatrix = attr(key=camel)
    distortion_coefficients: DistortionCoefficients = attr(is_dynamic=True, key=camel)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        fx: Optional[float] = None,
        fy: Optional[float] = None,
        cx: Optional[float] = None,
        cy: Optional[float] = None,
        skew: float = 0,
        *,
        camera_matrix: Optional[MatrixType] = None,
        **kwargs: float,
    ) -> None:
        self.camera_matrix = CameraMatrix(fx, fy, cx, cy, skew, matrix=camera_matrix)
        if kwargs:
            self.distortion_coefficients = DistortionCoefficients.loads(kwargs)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Loads CameraIntrinsics from a dict containing the information.

        Arguments:
            contents: A dict containig camera matrix and distortion coefficients.

        Returns:
            A :class:`CameraIntrinsics` instance containing information from
            the contents dict.

        Examples:
            >>> contents = {
            ...     "cameraMatrix": {
            ...         "fx": 1,
            ...         "fy": 2,
            ...         "cx": 3,
            ...         "cy": 4,
            ...     },
            ...     "distortionCoefficients": {
            ...         "p1": 1,
            ...         "p2": 2,
            ...         "k1": 3,
            ...         "k2": 4
            ...     },
            ... }
            >>> camera_intrinsics = CameraIntrinsics.loads(contents)
            >>> camera_intrinsics
            CameraIntrinsics(
                (camera_matrix): CameraMatrix(
                    (fx): 1,
                    (fy): 2,
                    (cx): 3,
                    (cy): 4,
                    (skew): 0
                ),
                (distortion_coefficients): DistortionCoefficients(
                    (p1): 1,
                    (p2): 2,
                    (k1): 3,
                    (k2): 4
                )
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the camera intrinsics into a dict.

        Returns:
            A dict containing camera intrinsics.

        Examples:
            >>> camera_intrinsics.dumps()
            {'cameraMatrix': {'fx': 1, 'fy': 2, 'cx': 3, 'cy': 4, 'skew': 3},
            'distortionCoefficients': {'p1': 5, 'k1': 6}}

        """
        return self._dumps()

    def set_camera_matrix(  # pylint: disable=[too-many-arguments, invalid-name]
        self,
        fx: Optional[float] = None,
        fy: Optional[float] = None,
        cx: Optional[float] = None,
        cy: Optional[float] = None,
        skew: float = 0,
        *,
        matrix: Optional[MatrixType] = None,
    ) -> None:
        """Set camera matrix of the camera intrinsics.

        Arguments:
            fx: The x axis focal length expressed in pixels.
            fy: The y axis focal length expressed in pixels.
            cx: The x coordinate of the so called principal point that should be in the center of
                the image.
            cy: The y coordinate of the so called principal point that should be in the center of
                the image.
            skew: It causes shear distortion in the projected image.
            matrix: Camera matrix in 3x3 sequence.

        Examples:
            >>> camera_intrinsics.set_camera_matrix(fx=11, fy=12, cx=13, cy=14, skew=15)
            >>> camera_intrinsics
            CameraIntrinsics(
                (camera_matrix): CameraMatrix(
                    (fx): 11,
                    (fy): 12,
                    (cx): 13,
                    (cy): 14,
                    (skew): 15
                ),
                (distortion_coefficients): DistortionCoefficients(
                    (p1): 1,
                    (p2): 2,
                    (k1): 3,
                    (k2): 4
                )
            )

        """
        self.camera_matrix = CameraMatrix(fx, fy, cx, cy, skew, matrix=matrix)

    def set_distortion_coefficients(self, **kwargs: float) -> None:
        """Set distortion coefficients of the camera intrinsics.

        Arguments:
            **kwargs: Contains p1, p2, ..., k1, k2, ...

        Examples:
            >>> camera_intrinsics.set_distortion_coefficients(p1=11, p2=12, k1=13, k2=14)
            >>> camera_intrinsics
            CameraIntrinsics(
                (camera_matrix): CameraMatrix(
                    (fx): 11,
                    (fy): 12,
                    (cx): 13,
                    (cy): 14,
                    (skew): 15
                ),
                (distortion_coefficients): DistortionCoefficients(
                    (p1): 11,
                    (p2): 12,
                    (k1): 13,
                    (k2): 14
                )
            )

        """
        self.distortion_coefficients = DistortionCoefficients(**kwargs)

    def project(self, point: Sequence[float], is_fisheye: bool = False) -> Vector2D:
        """Project a point to the pixel coordinates.

        If distortion coefficients are provided, distort the point before projection.

        Arguments:
            point: A Sequence containing coordinates of the point to be projected.
            is_fisheye: Whether the sensor is fisheye camera, default is False.

        Returns:
            The coordinates on the pixel plane where the point is projected to.

        Examples:
            Project a point with 2 dimensions.

            >>> camera_intrinsics.project((1, 2))
            Vector2D(137.0, 510.0)

            Project a point with 3 dimensions.

            >>> camera_intrinsics.project((1, 2, 3))
            Vector2D(6.300411522633745, 13.868312757201647)

            Project a point with 2 dimensions, fisheye is True

            >>> camera_intrinsics.project((1, 2), is_fisheye=True)
            Vector2D(9.158401093771875, 28.633604375087504)

        """
        if hasattr(self, "distortion_coefficients"):
            point = self.distortion_coefficients.distort(point, is_fisheye)
        return self.camera_matrix.project(point)
