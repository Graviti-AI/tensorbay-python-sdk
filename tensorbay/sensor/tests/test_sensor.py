#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from typing import Type

import pytest
from quaternion import quaternion

from ...geometry import Transform3D, Vector3D
from .. import (
    Camera,
    CameraIntrinsics,
    CameraMatrix,
    DistortionCoefficients,
    FisheyeCamera,
    Lidar,
    Radar,
    Sensor,
    Sensors,
    SensorType,
)

_TRANSLATION = Vector3D(1, 2, 3)
_ROTATION = quaternion(1, 2, 3, 4)

_LIDAR_DATA = {
    "name": "Lidar1",
    "type": "LIDAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}
_RADAR_DATA = {
    "name": "Radar1",
    "type": "RADAR",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}
_CAMERA_DATA = {
    "name": "Camera1",
    "type": "CAMERA",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
    "intrinsics": {
        "cameraMatrix": {"fx": 1, "fy": 1, "cx": 1, "cy": 1, "skew": 0},
        "distortionCoefficients": {"p1": 1, "p2": 1, "k1": 1, "k2": 1},
    },
}
_FISHEYE_CAMERA_DATA = {
    "name": "FisheyeCamera1",
    "type": "FISHEYE_CAMERA",
    "extrinsics": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1.0, "x": 2.0, "y": 3.0, "z": 4.0},
    },
}

_SENSORS_DATA = [
    _CAMERA_DATA,
    _FISHEYE_CAMERA_DATA,
    _LIDAR_DATA,
    _RADAR_DATA,
]


class TestSenorType:
    assert SensorType.LIDAR == SensorType("LIDAR")
    assert SensorType.RADAR == SensorType("RADAR")
    assert SensorType.CAMERA == SensorType("CAMERA")
    assert SensorType.FISHEYE_CAMERA == SensorType("FISHEYE_CAMERA")


class TestSensor:
    def test_new(self):
        with pytest.raises(TypeError):
            sensor = Sensor("Radar1")

    def test_loads(self):
        camera_1 = Sensor.loads(_CAMERA_DATA)

        assert camera_1.extrinsics == Transform3D(_TRANSLATION, _ROTATION)
        assert camera_1.intrinsics == CameraIntrinsics(
            fx=1, fy=1, cx=1, cy=1, skew=0, p1=1, p2=1, k1=1, k2=1
        )


class TestLidar:
    def test_init(self):
        lidar = Lidar("Lidar1")
        assert lidar.name == "Lidar1"

    def test_set_extrinsics(self):
        lidar_1 = Lidar("test")
        lidar_1.set_extrinsics()
        assert lidar_1.extrinsics == Transform3D()

        lidar_2 = Lidar("test")
        lidar_2.set_extrinsics(_TRANSLATION, _ROTATION)
        assert lidar_2.extrinsics == Transform3D(_TRANSLATION, _ROTATION)

    def test_set_translation(self):
        lidar = Lidar("test")
        lidar.set_translation(x=1, y=2, z=3)
        assert lidar.extrinsics.translation == _TRANSLATION

    def test_set_rotation(self):
        lidar = Lidar("test")
        lidar.set_rotation([1, 2, 3, 4])
        assert lidar.extrinsics.rotation == _ROTATION

    def test_dumps(self):
        lidar = Lidar("Lidar1")
        lidar.set_extrinsics(_TRANSLATION, _ROTATION)
        contents = lidar.dumps()
        assert contents == _LIDAR_DATA


class TestRadar:
    def test_init(self):
        radar = Radar("Radar1")
        assert radar.name == "Radar1"

    def test_set_extrinsics(self):
        radar_1 = Radar("test")
        radar_1.set_extrinsics()
        assert radar_1.extrinsics == Transform3D()

        radar_2 = Radar("test")
        radar_2.set_extrinsics(_TRANSLATION, _ROTATION)
        assert radar_2.extrinsics == Transform3D(_TRANSLATION, _ROTATION)

    def test_set_translation(self):
        radar = Radar("test")
        radar.set_translation(x=1, y=2, z=3)
        assert radar.extrinsics.translation == _TRANSLATION

    def test_set_rotation(self):
        radar = Radar("test")
        radar.set_rotation([1, 2, 3, 4])
        assert radar.extrinsics.rotation == _ROTATION

    def test_dumps(self):
        radar = Radar("Radar1")
        radar.set_extrinsics(_TRANSLATION, _ROTATION)
        contents = radar.dumps()
        assert contents == _RADAR_DATA


class TestCamera:
    def test_init(self):
        camera = Camera("Camera1")
        assert camera.name == "Camera1"

    def test_set_extrinsics(self):
        camera_1 = Camera("test")
        camera_1.set_extrinsics()
        assert camera_1.extrinsics == Transform3D()

        camera_2 = Camera("test")
        camera_2.set_extrinsics(_TRANSLATION, _ROTATION)
        assert camera_2.extrinsics == Transform3D(_TRANSLATION, _ROTATION)

    def test_set_translation(self):
        camera = Camera("test")
        camera.set_translation(x=1, y=2, z=3)
        assert camera.extrinsics.translation == _TRANSLATION

    def test_set_rotation(self):
        camera = Camera("test")
        camera.set_rotation([1, 2, 3, 4])
        assert camera.extrinsics.rotation == _ROTATION

    def test_set_camera_matrix(self):
        camera = Camera("test")
        camera.set_camera_matrix(fx=1, fy=2, cx=3, cy=4)
        assert camera.intrinsics.camera_matrix == CameraMatrix(fx=1, fy=2, cx=3, cy=4, skew=0)

    def test_set_distortion_coefficients(self):
        camera = Camera("test")
        with pytest.raises(ValueError):
            camera.set_distortion_coefficients(p1=1, p2=2, k1=3, k2=4)

        camera.set_camera_matrix(fx=1, fy=2, cx=3, cy=4)
        camera.set_distortion_coefficients(p1=1, p2=2, k1=3, k2=4)
        assert camera.intrinsics.distortion_coefficients == DistortionCoefficients(
            p1=1, p2=2, k1=3, k2=4
        )

    def test_dumps(self):
        camera = Camera("Camera1")
        camera.set_extrinsics(_TRANSLATION, _ROTATION)
        camera.set_camera_matrix(fx=1, fy=1, cx=1, cy=1)
        camera.set_distortion_coefficients(p1=1, p2=1, k1=1, k2=1)
        contents = camera.dumps()
        assert contents == _CAMERA_DATA


class TestFisheyeCamera:
    def test_init(self):
        fisheye_camera = FisheyeCamera("FisheyeCamera1")
        assert fisheye_camera.name == "FisheyeCamera1"

    def test_set_extrinsics(self):
        fisheye_camera_1 = FisheyeCamera("test")
        fisheye_camera_1.set_extrinsics()
        assert fisheye_camera_1.extrinsics == Transform3D()

        fisheye_camera_2 = FisheyeCamera("test")
        fisheye_camera_2.set_extrinsics(_TRANSLATION, _ROTATION)
        assert fisheye_camera_2.extrinsics == Transform3D(_TRANSLATION, _ROTATION)

    def test_set_translation(self):
        fisheye_camera = FisheyeCamera("test")
        fisheye_camera.set_translation(x=1, y=2, z=3)
        assert fisheye_camera.extrinsics.translation == _TRANSLATION

    def test_set_rotation(self):
        fisheye_camera = FisheyeCamera("test")
        fisheye_camera.set_rotation([1, 2, 3, 4])
        assert fisheye_camera.extrinsics.rotation == _ROTATION

    def test_dumps(self):
        fisheye_camera = FisheyeCamera("FisheyeCamera1")
        fisheye_camera.set_extrinsics(_TRANSLATION, _ROTATION)
        contents = fisheye_camera.dumps()
        assert contents == _FISHEYE_CAMERA_DATA


class TestSensors:
    def test_loads(self):
        sensors = Sensors.loads(_SENSORS_DATA)
        assert sensors[_LIDAR_DATA["name"]] == Lidar.loads(_LIDAR_DATA)
        assert sensors[_RADAR_DATA["name"]] == Radar.loads(_RADAR_DATA)
        assert sensors[_CAMERA_DATA["name"]] == Camera.loads(_CAMERA_DATA)
        assert sensors[_FISHEYE_CAMERA_DATA["name"]] == FisheyeCamera.loads(_FISHEYE_CAMERA_DATA)

    def test_dumps(self):
        sensors = Sensors()
        sensors.add(Lidar.loads(_LIDAR_DATA))
        sensors.add(Radar.loads(_RADAR_DATA))
        sensors.add(Camera.loads(_CAMERA_DATA))
        sensors.add(FisheyeCamera.loads(_FISHEYE_CAMERA_DATA))

        assert sensors.dumps() == _SENSORS_DATA
