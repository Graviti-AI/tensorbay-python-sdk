#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
import numpy as np
import pytest

from tensorbay.geometry import Vector2D
from tensorbay.sensor import CameraIntrinsics, CameraMatrix, DistortionCoefficients

_3x3_MATRIX = [[1, 2, 3], [0, 4, 5], [0, 0, 1]]
_3x3_NUMPY = np.array([[1.0, 2.0, 3.0], [0.0, 4.0, 5.0], [0.0, 0.0, 1.0]])

_CAMERA_MATRIX_DATA = {"fx": 2, "fy": 6, "cx": 4, "cy": 7, "skew": 3}

_CAMERA_MATRIX_NO_SKEW_DATA = {"fx": 2, "fy": 6, "cx": 4, "cy": 7}

_DISTORTIONCOEFFICIENTS_DATA = {"p1": 1, "p2": 2, "k1": 3, "k2": 4}

_CAMERAINTRINSICS_DATA = {
    "cameraMatrix": {"fx": 1, "fy": 2, "cx": 3, "cy": 4},
    "distortionCoefficients": {"p1": 1, "k1": 2},
}


class TestCameraMatrix:
    def test_init(self):
        with pytest.raises(TypeError):
            CameraMatrix()
        with pytest.raises(TypeError):
            CameraMatrix(fx=1, fy=2)

        camera_matrix_1 = CameraMatrix(matrix=_3x3_MATRIX)

        assert camera_matrix_1.fx == 1
        assert camera_matrix_1.fy == 4
        assert camera_matrix_1.cx == 3
        assert camera_matrix_1.cy == 5
        assert camera_matrix_1.skew == 2

        camera_matrix_1 = CameraMatrix(1, 2, 3, 4)
        assert camera_matrix_1.fx == 1
        assert camera_matrix_1.fy == 2
        assert camera_matrix_1.cx == 3
        assert camera_matrix_1.cy == 4
        assert camera_matrix_1.skew == 0

    def test_loads(self):
        cameramatrix = CameraMatrix.loads(_CAMERA_MATRIX_DATA)

        assert cameramatrix.fx == 2
        assert cameramatrix.fy == 6
        assert cameramatrix.cx == 4
        assert cameramatrix.cy == 7
        assert cameramatrix.skew == 3

    def test_eq(self):
        fx, fy, cx, cy, skew = 2, 6, 4, 7, 3

        camera_matrix_1 = CameraMatrix(fx=fx, fy=fy, cx=cx, cy=cy, skew=skew)
        camera_matrix_2 = CameraMatrix(fx=fx, fy=fy, cx=cx, cy=cy, skew=skew)
        camera_matrix_3 = CameraMatrix(matrix=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        assert (camera_matrix_1 == camera_matrix_2) == True
        assert (camera_matrix_1 == camera_matrix_3) == False

    def test_dumps(self):
        fx, fy, cx, cy, skew = 2, 6, 4, 7, 3
        camera_matrix_1 = CameraMatrix(fx=fx, fy=fy, cx=cx, cy=cy, skew=skew)
        assert camera_matrix_1.dumps() == _CAMERA_MATRIX_DATA

        camera_matrix_2 = CameraMatrix(fx=fx, fy=fy, cx=cx, cy=cy)
        assert camera_matrix_2.dumps() == _CAMERA_MATRIX_NO_SKEW_DATA

    def test_as_matrix(self):
        camera_matrix = CameraMatrix(matrix=_3x3_MATRIX).as_matrix()
        assert np.all(np.array(camera_matrix) == _3x3_NUMPY)

    def test_project(self):
        camera_matrix = CameraMatrix(matrix=_3x3_MATRIX)

        with pytest.raises(TypeError):
            camera_matrix.project([])
        with pytest.raises(TypeError):
            camera_matrix.project([1])
        with pytest.raises(TypeError):
            camera_matrix.project([1, 1, 1, 1])
        with pytest.raises(ZeroDivisionError):
            camera_matrix.project([0, 0, 0])

        assert camera_matrix.project([0, 0]) == Vector2D(3, 5)
        assert camera_matrix.project([1, 2]) == Vector2D(8, 13)
        assert camera_matrix.project([1, 2, 4]) == Vector2D(4.25, 7.0)


class TestDistortionCoefficients:
    def test_init(self):
        with pytest.raises(TypeError):
            DistortionCoefficients()
        with pytest.raises(TypeError):
            DistortionCoefficients(1, 2)

        distortion_coefficients = DistortionCoefficients(p1=1, k1=2)

        assert distortion_coefficients.p1 == 1
        assert distortion_coefficients.k1 == 2

    def test_eq(self):
        distortion_coefficients_1 = DistortionCoefficients(p1=1, k1=2)
        distortion_coefficients_2 = DistortionCoefficients(p1=1, k1=2)
        distortion_coefficients_3 = DistortionCoefficients(p1=2, k1=3)

        assert (distortion_coefficients_1 == distortion_coefficients_2) == True
        assert (distortion_coefficients_1 == distortion_coefficients_3) == False

    def test_distortion_generator(self):
        distortion_generator_p = DistortionCoefficients._distortion_generator(
            "p", _DISTORTIONCOEFFICIENTS_DATA
        )

        contents_p = list(distortion_generator_p)
        assert contents_p == [("p1", 1), ("p2", 2)]

        distortion_generator_with_v = DistortionCoefficients._distortion_generator(
            "v", _DISTORTIONCOEFFICIENTS_DATA
        )

        contents_v = list(distortion_generator_with_v)
        assert contents_v == []

    def test_repr_attrs(self):
        distortion_coefficients = DistortionCoefficients(p1=1, k1=2, p2=3, k2=4, k3=5, p3=6)
        distortion_names = list(distortion_coefficients._repr_attrs)

        assert (distortion_names == ["p1", "p2", "p3", "k1", "k2", "k3"]) == True

    def test_calculate_radial_distortion(self):
        distortion_coefficients = DistortionCoefficients(p1=1, k1=2)
        fisheye_true = distortion_coefficients._calculate_radial_distortion(r2=1, is_fisheye=True)
        fisheye_false = distortion_coefficients._calculate_radial_distortion(r2=1, is_fisheye=False)

        assert fisheye_true == 1.7543443096568176
        assert fisheye_false == 3.0

    def test_calculate_tangential_distortion(self):
        distortion_coefficients = DistortionCoefficients(p1=1, p2=2, k1=1)
        fisheye_true = distortion_coefficients._calculate_tangential_distortion(
            r2=1, x2=2, y2=3, xy2=4, is_fisheye=True
        )
        assert fisheye_true == (0, 0)

        fisheye_false = distortion_coefficients._calculate_tangential_distortion(
            r2=1, x2=2, y2=3, xy2=4, is_fisheye=False
        )
        assert fisheye_false == (14, 15)

        distortion_coefficients_p1 = DistortionCoefficients(p1=1, k1=1)
        with pytest.raises(AttributeError):
            distortion_coefficients_p1._calculate_tangential_distortion(
                r2=1, x2=2, y2=3, xy2=4, is_fisheye=False
            )

    def test_list_distortions(self):
        distortion_coefficients = DistortionCoefficients(p1=1, p2=2, k1=3, k2=4)
        result_p = distortion_coefficients._list_distortions("p")

        assert list(result_p) == [1.0, 2.0]

    def test_loads(self):
        distortion_coefficients = DistortionCoefficients.loads(_DISTORTIONCOEFFICIENTS_DATA)

        assert distortion_coefficients.p1 == _DISTORTIONCOEFFICIENTS_DATA["p1"]
        assert distortion_coefficients.p2 == _DISTORTIONCOEFFICIENTS_DATA["p2"]
        assert distortion_coefficients.k1 == _DISTORTIONCOEFFICIENTS_DATA["k1"]
        assert distortion_coefficients.k2 == _DISTORTIONCOEFFICIENTS_DATA["k2"]

    def test_dumps(self):
        distortion_coefficients = DistortionCoefficients(p1=1.0, p2=2.0, k1=3.0, k2=4.0)
        assert distortion_coefficients.dumps() == _DISTORTIONCOEFFICIENTS_DATA

    def test_distort(self):
        distortion_coefficients = DistortionCoefficients(p1=1.0, p2=2.0, k1=3.0, k2=4.0)

        with pytest.raises(TypeError):
            distortion_coefficients.distort((1.0, 2.0, 3.0, 4.0), is_fisheye=True)

        distored_2d_fisheye_true_1 = distortion_coefficients.distort((1.0, 2.0), is_fisheye=True)
        distored_2d_fisheye_true_2 = distortion_coefficients.distort(
            (1.0, 2.0, 3.0), is_fisheye=True
        )
        assert distored_2d_fisheye_true_1 == Vector2D(6.158401093771876, 12.316802187543752)
        assert distored_2d_fisheye_true_2 == Vector2D(0.83187700005734, 1.66375400011468)

        distored_2d_fisheye_false_1 = distortion_coefficients.distort((1.0, 2.0), is_fisheye=False)
        distored_2d_fisheye_false_2 = distortion_coefficients.distort(
            (1.0, 2.0, 3.0), is_fisheye=False
        )
        assert distored_2d_fisheye_false_1 == Vector2D(134.0, 253.0)
        assert distored_2d_fisheye_false_2 == Vector2D(3.3004115226337447, 4.934156378600823)


class TestCameraIntrinsics:
    def test_init(self):
        with pytest.raises(TypeError):
            CameraIntrinsics(p1=1, p2=2, k1=3, k2=4)

        camera_intrinsics_1 = CameraIntrinsics(fx=1, fy=2, cx=3, cy=4, p1=5, k1=6)

        assert camera_intrinsics_1.camera_matrix.fx == 1
        assert camera_intrinsics_1.camera_matrix.fy == 2
        assert camera_intrinsics_1.camera_matrix.cx == 3
        assert camera_intrinsics_1.camera_matrix.cy == 4
        assert camera_intrinsics_1.camera_matrix.skew == 0

        assert camera_intrinsics_1.distortion_coefficients.p1 == 5
        assert camera_intrinsics_1.distortion_coefficients.k1 == 6

        camera_intrinsics_2 = CameraIntrinsics(
            camera_matrix=[[2, 3, 4], [0, 5, 6], [0, 0, 1]], p1=7, k1=8
        )

        assert camera_intrinsics_2.camera_matrix.fx == 2
        assert camera_intrinsics_2.camera_matrix.fy == 5
        assert camera_intrinsics_2.camera_matrix.cx == 4
        assert camera_intrinsics_2.camera_matrix.cy == 6
        assert camera_intrinsics_2.camera_matrix.skew == 3

        assert camera_intrinsics_2.distortion_coefficients.p1 == 7
        assert camera_intrinsics_2.distortion_coefficients.k1 == 8

        camera_intrinsics_3 = CameraIntrinsics(fx=1, fy=2, cx=3, cy=4)
        with pytest.raises(AttributeError):
            camera_intrinsics_3.distortion_coefficients

    def test_loads(self):
        camera_intrinsics = CameraIntrinsics.loads(_CAMERAINTRINSICS_DATA)

        assert camera_intrinsics.camera_matrix.fx == _CAMERAINTRINSICS_DATA["cameraMatrix"]["fx"]
        assert camera_intrinsics.camera_matrix.fy == _CAMERAINTRINSICS_DATA["cameraMatrix"]["fy"]
        assert camera_intrinsics.camera_matrix.cx == _CAMERAINTRINSICS_DATA["cameraMatrix"]["cx"]
        assert camera_intrinsics.camera_matrix.cy == _CAMERAINTRINSICS_DATA["cameraMatrix"]["cy"]
        assert camera_intrinsics.camera_matrix.skew == 0
        assert (
            camera_intrinsics.distortion_coefficients.p1
            == _CAMERAINTRINSICS_DATA["distortionCoefficients"]["p1"]
        )
        assert (
            camera_intrinsics.distortion_coefficients.k1
            == _CAMERAINTRINSICS_DATA["distortionCoefficients"]["k1"]
        )

    def test_eq(self):
        camera_intrinsics_1 = CameraIntrinsics(fx=1, fy=2, cx=3, cy=4, skew=0, p1=1, k1=2)
        camera_intrinsics_2 = CameraIntrinsics(fx=1, fy=2, cx=3, cy=4, skew=0, p1=1, k1=2)
        camera_intrinsics_3 = CameraIntrinsics(
            camera_matrix=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], p1=0, k1=0
        )

        assert (camera_intrinsics_1 == camera_intrinsics_2) == True
        assert (camera_intrinsics_1 == camera_intrinsics_3) == False

    def test_dumps(self):
        camera_intrinsics = CameraIntrinsics(fx=1, fy=2, cx=3, cy=4, skew=0, p1=1, k1=2)
        assert camera_intrinsics.dumps() == _CAMERAINTRINSICS_DATA

    def test_set_camera_matrix(self):
        camera_intrinsics = CameraIntrinsics(fx=0, fy=0, cx=0, cy=0, p1=0, p2=0, k1=0, k2=0)
        camera_intrinsics.set_camera_matrix(fx=2, fy=6, cx=4, cy=7, skew=3)

        assert camera_intrinsics.camera_matrix == CameraMatrix(fx=2, fy=6, cx=4, cy=7, skew=3)

    def test_set_distortion_coefficients(self):
        camera_intrinsics = CameraIntrinsics(fx=0, fy=0, cx=0, cy=0, p1=0, p2=0, k1=0, k2=0)
        camera_intrinsics.set_distortion_coefficients(p1=1, p2=2, k1=1, k2=2)

        assert camera_intrinsics.distortion_coefficients == DistortionCoefficients(
            p1=1, p2=2, k1=1, k2=2
        )

    def test_project(self):
        camera_intrinsics = CameraIntrinsics(
            camera_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], p1=1, p2=1, k1=1
        )

        point_1_fisheye_true = camera_intrinsics.project((1, 2), is_fisheye=True)
        point_2_fisheye_true = camera_intrinsics.project((1, 2, 3), is_fisheye=True)
        assert point_1_fisheye_true == Vector2D(1.195033740719647, 2.390067481439294)
        assert point_2_fisheye_true == Vector2D(0.4039719111977248, 0.8079438223954496)

        point_1_fisheye_false = camera_intrinsics.project((1, 2), is_fisheye=False)
        point_2_fisheye_false = camera_intrinsics.project((1, 2, 3), is_fisheye=False)
        assert point_1_fisheye_false == Vector2D(17.0, 29.0)
        assert point_2_fisheye_false == Vector2D(1.740740740740741, 2.9259259259259256)
