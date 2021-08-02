#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""SensorType, Sensor, Lidar, Radar, Camera, FisheyeCamera and Sensors.

:class:`SensorType` is an enumeration type. It includes 'LIDAR', 'RADAR', 'CAMERA' and
'FISHEYE_CAMERA'.

:class:`Sensor` defines the concept of sensor. It includes name, description, translation
and rotation.

A :class:`Sensor` class can be initialized by :meth:`Sensor.__init__()` or
:meth:`Sensor.loads()` method.

:class:`Lidar` defines the concept of lidar. It is a kind of sensor for measuring distances by
illuminating the target with laser light and measuring the reflection.

:class:`Radar` defines the concept of radar. It is a detection system that uses radio waves to
determine the range, angle, or velocity of objects.

:class:`Camera` defines the concept of camera. It includes name, description, translation,
rotation, cameraMatrix and distortionCoefficients.

:class:`FisheyeCamera` defines the concept of fisheye camera. It is an ultra wide-angle lens that
produces strong visual distortion intended to create a wide panoramic or hemispherical image.

:class:`Sensors` represent all the sensors in a :class:`~tensorbay.dataset.segment.FusionSegment`.

"""

import warnings
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..geometry import Transform3D
from ..utility import (
    MatrixType,
    NameMixin,
    ReprType,
    SortedNameList,
    TypeEnum,
    TypeMixin,
    TypeRegister,
    common_loads,
)
from .intrinsics import CameraIntrinsics

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from quaternion import quaternion as Quaternion

_T = TypeVar("_T", bound="Sensor")


class SensorType(TypeEnum):
    """SensorType is an enumeration type.

    It includes 'LIDAR', 'RADAR', 'CAMERA' and 'FISHEYE_CAMERA'.

    Examples:
        >>> SensorType.CAMERA
        <SensorType.CAMERA: 'CAMERA'>
        >>> SensorType["CAMERA"]
        <SensorType.CAMERA: 'CAMERA'>

        >>> SensorType.CAMERA.name
        'CAMERA'
        >>> SensorType.CAMERA.value
        'CAMERA'

    """

    LIDAR = "LIDAR"
    RADAR = "RADAR"
    CAMERA = "CAMERA"
    FISHEYE_CAMERA = "FISHEYE_CAMERA"


class Sensor(NameMixin, TypeMixin[SensorType]):
    """Sensor defines the concept of sensor.

    :class:`Sensor` includes name, description, translation and rotation.

    Arguments:
        name: :class:`Sensor`'s name.

    Raises:
        TypeError: Can not instantiate abstract class :class:`Sensor`.

    Attributes:
        extrinsics: The translation and rotation of the sensor.

    """

    _Type = Union["Radar", "Lidar", "FisheyeCamera", "Camera"]

    _repr_type = ReprType.INSTANCE
    _repr_attrs: Tuple[str, ...] = ("extrinsics",)
    _repr_maxlevel = 3

    extrinsics: Transform3D

    def __new__(
        cls: Type[_T],
        name: str,  # pylint: disable=unused-argument
    ) -> _T:
        """Create a new instance of Sensor.

        Arguments:
            name: :class:`Sensor`'s name.

        Returns:
            A :class:`Sensor` instance containing the :class:`sensor`'s name.

        Raises:
            TypeError: Can't instantiate abstract class :class:`Sensor`.

        """
        if cls is Sensor:
            raise TypeError("Can't instantiate abstract class Sensor")

        obj: _T = object.__new__(cls)
        return obj

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        extrinsics = contents.get("extrinsics")
        if extrinsics:
            self.extrinsics = Transform3D.loads(contents["extrinsics"])

    @staticmethod
    def loads(contents: Dict[str, Any]) -> "_Type":
        """Loads a Sensor from a dict containing the sensor information.

        Arguments:
            contents: A dict containing name, description and sensor extrinsics.

        Returns:
            A :class:`Sensor` instance containing the information from the contents dict.

        Examples:
            >>> contents = {
            ...     "name": "Lidar1",
            ...     "type": "LIDAR",
            ...     "extrinsics": {
            ...         "translation": {"x": 1.1, "y": 2.2, "z": 3.3},
            ...         "rotation": {"w": 1.1, "x": 2.2, "y": 3.3, "z": 4.4},
            ...     },
            ... }
            >>> sensor = Sensor.loads(contents)
            >>> sensor
            Lidar("Lidar1")(
                (extrinsics): Transform3D(
                    (translation): Vector3D(1.1, 2.2, 3.3),
                    (rotation): quaternion(1.1, 2.2, 3.3, 4.4)
                )
            )

        """
        sensor: "Sensor._Type" = common_loads(SensorType(contents["type"]).type, contents)
        return sensor

    def dumps(self) -> Dict[str, Any]:
        """Dumps the sensor into a dict.

        Returns:
            A dict containing the information of the sensor.

        Examples:
            >>> # sensor is the object initialized from self.loads() method.
            >>> sensor.dumps()
            {
                'name': 'Lidar1',
                'type': 'LIDAR',
                'extrinsics': {'translation': {'x': 1.1, 'y': 2.2, 'z': 3.3},
                'rotation': {'w': 1.1, 'x': 2.2, 'y': 3.3, 'z': 4.4}
                }
            }

        """
        contents: Dict[str, Any] = super()._dumps()
        contents["type"] = self.enum.value
        if hasattr(self, "extrinsics"):
            contents["extrinsics"] = self.extrinsics.dumps()

        return contents

    def set_extrinsics(
        self,
        translation: Iterable[float] = (0, 0, 0),
        rotation: Transform3D.RotationType = (1, 0, 0, 0),
        *,
        matrix: Optional[MatrixType] = None,
    ) -> None:
        """Set the extrinsics of the sensor.

        Arguments:
            translation: Translation parameters.
            rotation: Rotation in a sequence of [w, x, y, z] or numpy quaternion.
            matrix: A 3x4 or 4x4 transform matrix.

        Examples:
            >>> sensor.set_extrinsics(translation=translation, rotation=rotation)
            >>> sensor
            Lidar("Lidar1")(
                (extrinsics): Transform3D(
                    (translation): Vector3D(1, 2, 3),
                    (rotation): quaternion(1, 2, 3, 4)
                )
            )

        """
        self.extrinsics = Transform3D(translation, rotation, matrix=matrix)

    def set_translation(self, x: float, y: float, z: float) -> None:
        """Set the translation of the sensor.

        Arguments:
            x: The x coordinate of the translation.
            y: The y coordinate of the translation.
            z: The z coordinate of the translation.

        Examples:
            >>> sensor.set_translation(x=2, y=3, z=4)
            >>> sensor
            Lidar("Lidar1")(
                (extrinsics): Transform3D(
                    (translation): Vector3D(2, 3, 4),
                    ...
                )
            )

        """
        if not hasattr(self, "extrinsics"):
            self.extrinsics = Transform3D()
        self.extrinsics.set_translation(x, y, z)

    def set_rotation(
        self,
        w: Optional[float] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        *,
        quaternion: Optional[Quaternion] = None,
    ) -> None:
        """Set the rotation of the sensor.

        Arguments:
            w: The w componet of the roation quaternion.
            x: The x componet of the roation quaternion.
            y: The y componet of the roation quaternion.
            z: The z componet of the roation quaternion.
            quaternion: Numpy quaternion representing the rotation.

        Examples:
            >>> sensor.set_rotation(2, 3, 4, 5)
            >>> sensor
            Lidar("Lidar1")(
                (extrinsics): Transform3D(
                    ...
                    (rotation): quaternion(2, 3, 4, 5)
                )
            )

        """
        if not hasattr(self, "extrinsics"):
            self.extrinsics = Transform3D()
        self.extrinsics.set_rotation(w, x, y, z, quaternion=quaternion)


@TypeRegister(SensorType.LIDAR)
class Lidar(Sensor):
    """Lidar defines the concept of lidar.

    :class:`Lidar` is a kind of sensor for measuring distances by illuminating the target
    with laser light and measuring the reflection.

    Examples:
        >>> lidar = Lidar("Lidar1")
        >>> lidar.set_extrinsics(translation=translation, rotation=rotation)
        >>> lidar
        Lidar("Lidar1")(
            (extrinsics): Transform3D(
                (translation): Vector3D(1, 2, 3),
                (rotation): quaternion(1, 2, 3, 4)
            )
        )

    """


@TypeRegister(SensorType.RADAR)
class Radar(Sensor):
    """Radar defines the concept of radar.

    :class:`Radar` is a detection system that uses radio waves to determine the range, angle,
    or velocity of objects.

    Examples:
        >>> radar = Radar("Radar1")
        >>> radar.set_extrinsics(translation=translation, rotation=rotation)
        >>> radar
        Radar("Radar1")(
            (extrinsics): Transform3D(
                (translation): Vector3D(1, 2, 3),
                (rotation): quaternion(1, 2, 3, 4)
            )
        )

    """


@TypeRegister(SensorType.CAMERA)
class Camera(Sensor):
    """Camera defines the concept of camera.

    :class:`Camera` includes name, description, translation, rotation, cameraMatrix
    and distortionCoefficients.

    Attributes:
        extrinsics: The translation and rotation of the camera.
        intrinsics: The camera matrix and distortion coefficients of the camera.

    Examples:
        >>> from tensorbay.geometry import Vector3D
        >>> from numpy import quaternion
        >>> camera = Camera('Camera1')
        >>> translation = Vector3D(1, 2, 3)
        >>> rotation = quaternion(1, 2, 3, 4)
        >>> camera.set_extrinsics(translation=translation, rotation=rotation)
        >>> camera.set_camera_matrix(fx=1.1, fy=1.1, cx=1.1, cy=1.1)
        >>> camera.set_distortion_coefficients(p1=1.2, p2=1.2, k1=1.2, k2=1.2)
        >>> camera
        Camera("Camera1")(
            (extrinsics): Transform3D(
                (translation): Vector3D(1, 2, 3),
                (rotation): quaternion(1, 2, 3, 4)
            ),
            (intrinsics): CameraIntrinsics(
                (camera_matrix): CameraMatrix(
                    (fx): 1.1,
                    (fy): 1.1,
                    (cx): 1.1,
                    (cy): 1.1,
                    (skew): 0
                ),
                (distortion_coefficients): DistortionCoefficients(
                    (p1): 1.2,
                    (p2): 1.2,
                    (k1): 1.2,
                    (k2): 1.2
                )
            )
        )

    """

    _T = TypeVar("_T", bound="Camera")

    _repr_attrs = Sensor._repr_attrs + ("intrinsics",)

    intrinsics: CameraIntrinsics

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        intrinsics = contents.get("intrinsics")
        if intrinsics:
            self.intrinsics = CameraIntrinsics.loads(contents["intrinsics"])

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a Camera from a dict containing the camera information.

        Arguments:
            contents: A dict containing name, description, extrinsics and intrinsics.

        Returns:
            A :class:`Camera` instance containing information from contents dict.

        Examples:
            >>> contents = {
            ...     "name": "Camera1",
            ...     "type": "CAMERA",
            ...     "extrinsics": {
            ...           "translation": {"x": 1, "y": 2, "z": 3},
            ...           "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
            ...     },
            ...     "intrinsics": {
            ...         "cameraMatrix": {"fx": 1, "fy": 1, "cx": 1, "cy": 1, "skew": 0},
            ...         "distortionCoefficients": {"p1": 1, "p2": 1, "k1": 1, "k2": 1},
            ...     },
            ... }
            >>> Camera.loads(contents)
            Camera("Camera1")(
                    (extrinsics): Transform3D(
                        (translation): Vector3D(1, 2, 3),
                        (rotation): quaternion(1, 2, 3, 4)
                    ),
                    (intrinsics): CameraIntrinsics(
                        (camera_matrix): CameraMatrix(
                            (fx): 1,
                            (fy): 1,
                            (cx): 1,
                            (cy): 1,
                            (skew): 0
                        ),
                        (distortion_coefficients): DistortionCoefficients(
                            (p1): 1,
                            (p2): 1,
                            (k1): 1,
                            (k2): 1
                        )
                    )
                )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the camera into a dict.

        Returns:
            A dict containing name, description, extrinsics and intrinsics.

        Examples:
            >>> camera.dumps()
            {
                'name': 'Camera1',
                'type': 'CAMERA',
                'extrinsics': {
                    'translation': {'x': 1, 'y': 2, 'z': 3},
                    'rotation': {'w': 1.0, 'x': 2.0, 'y': 3.0, 'z': 4.0}
                },
                'intrinsics': {
                    'cameraMatrix': {'fx': 1, 'fy': 1, 'cx': 1, 'cy': 1, 'skew': 0},
                    'distortionCoefficients': {'p1': 1, 'p2': 1, 'k1': 1, 'k2': 1}
                }
            }

        """
        contents = super().dumps()
        if hasattr(self, "intrinsics"):
            contents["intrinsics"] = self.intrinsics.dumps()
        return contents

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
        """Set camera matrix.

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
            >>> camera.set_camera_matrix(fx=1.1, fy=2.2, cx=3.3, cy=4.4)
            >>> camera
            Camera("Camera1")(
                ...
                (intrinsics): CameraIntrinsics(
                    (camera_matrix): CameraMatrix(
                        (fx): 1.1,
                        (fy): 2.2,
                        (cx): 3.3,
                        (cy): 4.4,
                        (skew): 0
                    ),
                    ...
                    )
                )
            )

        """
        if not hasattr(self, "intrinsics"):
            self.intrinsics = CameraIntrinsics(fx, fy, cx, cy, skew, camera_matrix=matrix)
            return

        self.intrinsics.set_camera_matrix(fx, fy, cx, cy, skew, matrix=matrix)

    def set_distortion_coefficients(self, **kwargs: float) -> None:
        """Set distortion coefficients.

        Arguments:
            **kwargs: Float values to set distortion coefficients.

        Raises:
            ValueError: When intrinsics is not set yet.

        Examples:
            >>> camera.set_distortion_coefficients(p1=1.1, p2=2.2, k1=3.3, k2=4.4)
            >>> camera
            Camera("Camera1")(
                ...
                (intrinsics): CameraIntrinsics(
                    ...
                    (distortion_coefficients): DistortionCoefficients(
                        (p1): 1.1,
                        (p2): 2.2,
                        (k1): 3.3,
                        (k2): 4.4
                    )
                )
            )

        """
        if not hasattr(self, "intrinsics"):
            raise ValueError("Camera matrix of camera intrinsics must be set first.")
        self.intrinsics.set_distortion_coefficients(**kwargs)


@TypeRegister(SensorType.FISHEYE_CAMERA)
class FisheyeCamera(Camera):  # pylint: disable=too-many-ancestors
    """FisheyeCamera defines the concept of fisheye camera.

    Fisheye camera is an ultra wide-angle lens that produces strong visual distortion intended
    to create a wide panoramic or hemispherical image.

    Examples:
        >>> fisheye_camera = FisheyeCamera("FisheyeCamera1")
        >>> fisheye_camera.set_extrinsics(translation=translation, rotation=rotation)
        >>> fisheye_camera
        FisheyeCamera("FisheyeCamera1")(
            (extrinsics): Transform3D(
                (translation): Vector3D(1, 2, 3),
                (rotation): quaternion(1, 2, 3, 4)
            )
        )

    """


class Sensors(SortedNameList[Sensor._Type]):  # pylint: disable=protected-access
    """This class represents all sensors in a :class:`~tensorbay.dataset.segment.FusionSegment`."""

    _T = TypeVar("_T", bound="Sensors")

    def _loads(self, contents: List[Dict[str, Any]]) -> None:
        self._data = []
        self._names = []
        for sensor_info in contents:
            self.add(Sensor.loads(sensor_info))

    @classmethod
    def loads(cls: Type[_T], contents: List[Dict[str, Any]]) -> _T:
        """Loads a :class:`Sensors` instance from the given contents.

        Arguments:
            contents: A list of dict containing the sensors information in a fusion segment,
                whose format should be like::

                    [
                        {
                            "name": <str>
                            "type": <str>
                            "extrinsics": {
                                "translation": {
                                    "x": <float>
                                    "y": <float>
                                    "z": <float>
                                },
                                "rotation": {
                                    "w": <float>
                                    "x": <float>
                                    "y": <float>
                                    "z": <float>
                                },
                            },
                            "intrinsics": {           --- only for cameras
                                "cameraMatrix": {
                                    "fx": <float>
                                    "fy": <float>
                                    "cx": <float>
                                    "cy": <float>
                                    "skew": <float>
                                }
                                "distortionCoefficients": {
                                    "k1": <float>
                                    "k2": <float>
                                    "p1": <float>
                                    "p2": <float>
                                    ...
                                }
                            },
                            "desctiption": <str>
                        },
                        ...
                    ]

        Returns:
            The loaded :class:`Sensors` instance.

        """
        return common_loads(cls, contents)

    def dumps(self) -> List[Dict[str, Any]]:
        """Return the information of all the sensors.

        Returns:
            A list of dict containing the information of all sensors::

                [
                    {
                        "name": <str>
                        "type": <str>
                        "extrinsics": {
                            "translation": {
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                            "rotation": {
                                "w": <float>
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                        },
                        "intrinsics": {           --- only for cameras
                            "cameraMatrix": {
                                "fx": <float>
                                "fy": <float>
                                "cx": <float>
                                "cy": <float>
                                "skew": <float>
                            }
                            "distortionCoefficients": {
                                "k1": <float>
                                "k2": <float>
                                "p1": <float>
                                "p2": <float>
                                ...
                            }
                        },
                        "desctiption": <str>
                    },
                    ...
                ]

        """
        return [sensor.dumps() for sensor in self._data]
