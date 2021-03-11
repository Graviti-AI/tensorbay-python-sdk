#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""SensorType, Sensor, Lidar, Radar, Camera and FisheyeCamera.

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

"""

from typing import Any, Dict, Iterable, Optional, Sequence, Tuple, Type, TypeVar, Union

from ..geometry import Transform3D
from ..utility import NameMixin, ReprType, TypeEnum, TypeMixin, TypeRegister, common_loads
from .intrinsics import CameraIntrinsics

_T = TypeVar("_T", bound="Sensor")


class SensorType(TypeEnum):
    """SensorType is an enumeration type.

    It includes 'LIDAR', 'RADAR', 'CAMERA' and 'FISHEYE_CAMERA'.

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
        if "extrinsics" in contents:
            self.extrinsics = Transform3D.loads(contents["extrinsics"])

    @staticmethod
    def loads(contents: Dict[str, Any]) -> "_Type":
        """Loads a Sensor from a dict containing the sensor information.

        Arguments:
            contents: A dict containing name, description and sensor extrinsics.

        Returns:
            A :class:`Sensor` instance containing the information from the contents dict.

        """
        sensor: "Sensor._Type" = common_loads(SensorType(contents["type"]).type, contents)
        return sensor

    def dumps(self) -> Dict[str, Any]:
        """Dumps the sensor into a dict.

        Returns:
            A dict containing the information of the sensor.

        """
        contents: Dict[str, Any] = super()._dumps()
        contents["type"] = self.enum.value
        if hasattr(self, "extrinsics"):
            contents["extrinsics"] = self.extrinsics.dumps()

        return contents

    def set_extrinsics(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Iterable[float] = (0, 0, 0),
        rotation: Transform3D.RotationType = (1, 0, 0, 0),
    ) -> None:
        """Set the extrinsics of the sensor.

        Arguments:
            transform: A ``Transform3D`` object representing the extrinsics.
            translation: Translation parameters.
            rotation: Rotation in a sequence of [w, x, y, z] or 3x3 rotation matrix
                or numpy quaternion.

        """
        self.extrinsics = Transform3D(transform, translation=translation, rotation=rotation)

    def set_translation(self, x: float, y: float, z: float) -> None:
        """Set the translation of the sensor.

        Arguments:
            x: The x coordinate of the translation.
            y: The y coordinate of the translation.
            z: The z coordinate of the translation.

                    sensor.set_translation(x=1, y=2, z=3)

        """
        if not hasattr(self, "extrinsics"):
            self.extrinsics = Transform3D()
        self.extrinsics.set_translation(x, y, z)

    def set_rotation(self, rotation: Transform3D.RotationType) -> None:
        """Set the rotation of the sensor.

        Arguments:
            rotation: Rotation in a sequence of [w, x, y, z] or numpy quaternion.

        """
        if not hasattr(self, "extrinsics"):
            self.extrinsics = Transform3D()
        self.extrinsics.set_rotation(rotation)


@TypeRegister(SensorType.LIDAR)
class Lidar(Sensor):
    """Lidar defines the concept of lidar.

    :class:`Lidar` is a kind of sensor for measuring distances by illuminating the target
    with laser light and measuring the reflection.

    """


@TypeRegister(SensorType.RADAR)
class Radar(Sensor):
    """Radar defines the concept of radar.

    :class:`Radar` is a detection system that uses radio waves to determine the range, angle,
    or velocity of objects.

    """


@TypeRegister(SensorType.CAMERA)
class Camera(Sensor):
    """Camera defines the concept of camera.

    :class:`Camera` includes name, description, translation, rotation, cameraMatrix
    and distortionCoefficients.

    Attributes:
        extrinsics: The translation and rotation of the camera.
        intrinsics: The camera matrix and distortion coefficients of the camera.

    """

    _T = TypeVar("_T", bound="Camera")

    _repr_attrs = Sensor._repr_attrs + ("intrinsics",)

    intrinsics: CameraIntrinsics

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        if "intrinsics" in contents:
            self.intrinsics = CameraIntrinsics.loads(contents["intrinsics"])

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a Camera from a dict containing the camera information.

        Arguments:
            contents: A dict containing name, description, extrinsics and intrinsics.

        Returns:
            A :class:`Camera` instance containing information from contents dict.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the camera into a dict.

        Returns:
            A dict containing name, description, extrinsics and intrinsics.

        """
        contents = super().dumps()
        if hasattr(self, "intrinsics"):
            contents["intrinsics"] = self.intrinsics.dumps()
        return contents

    def set_camera_matrix(
        self,
        matrix: Optional[Sequence[Sequence[float]]] = None,
        **kwargs: float,
    ) -> None:
        """Set camera matrix.

        Arguments:
            matrix: A 3x3 Sequence of camera matrix.
            **kwargs: Other float values to set camera matrix.

        """
        if not hasattr(self, "intrinsics"):
            self.intrinsics = CameraIntrinsics(matrix, _init_distortion=False, **kwargs)
            return

        self.intrinsics.set_camera_matrix(matrix, **kwargs)

    def set_distortion_coefficients(self, **kwargs: float) -> None:
        """Set distortion coefficients.

        Arguments:
            **kwargs: Float values to set distortion coefficients.

        Raises:
            ValueError: When intrinsics is not set yet.

        """
        if not hasattr(self, "intrinsics"):
            raise ValueError("Camera matrix of camera intrinsics must be set first.")
        self.intrinsics.set_distortion_coefficients(**kwargs)


@TypeRegister(SensorType.FISHEYE_CAMERA)
class FisheyeCamera(Camera):  # pylint: disable=too-many-ancestors
    """FisheyeCamera defines the concept of fisheye camera.

    Fisheye camera is an ultra wide-angle lens that produces strong visual distortion intended
    to create a wide panoramic or hemispherical image.

    """
