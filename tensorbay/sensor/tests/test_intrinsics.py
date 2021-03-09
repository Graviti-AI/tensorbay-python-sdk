#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import numpy as np
import pytest

from ...geometry import Vector2D
from .. import CameraIntrinsics as CI
from .. import CameraMatrix as CM
from .. import DistortionCoefficients

_CAMERA_MATRIX_DIC = {"fx": 2, "fy": 6, "cx": 4, "cy": 7, "skew": 3}
_CAMERA_MATRIX_DATA_NP = np.array([[2.0, 3.0, 4.0], [0.0, 7.0, 7.0], [0.0, 0.0, 1.0]])
_CAMERA_MATRIX_DATA = [[2, 3, 4], [5, 6, 7], [8, 9, 10]]

_DISTORTIONCOEFFICIENTS_DATA = {"p1": 1.0, "p2": 2.0, "k1": 1.0, "k2": 2.0}
_CAMERAINTRINSICS_DATA = {
    "cameraMatrix": {"fx": 1.0, "fy": 2.0, "cx": 3.0, "cy": 4.0, "skew": 0},
    "distortionCoefficients": {"p1": 1},
}


class TestCameraMatrix:
    def test__init__(self):
        fx, fy, cx, cy, skew = 2, 6, 4, 7, 3

        with pytest.raises(TypeError):
            CM()
        with pytest.raises(TypeError):
            CM(fx=2, fy=6)
        with pytest.raises(TypeError):
            CM(2, 6, 4, 7, 3)

        cameramatrix = CM(_CAMERA_MATRIX_DATA)
        assert cameramatrix.fx == fx
        assert cameramatrix.fy == fy
        assert cameramatrix.cx == cx
        assert cameramatrix.cy == cy
        assert cameramatrix.skew == skew

    def test_loads_and_dumps(self):
        cameramatrix = CM.loads(_CAMERA_MATRIX_DIC)
        assert cameramatrix.dumps() == _CAMERA_MATRIX_DIC

    def test_as_matrix(self):
        cameramatrix = CM(_CAMERA_MATRIX_DATA)
        cameramatrix.as_matrix() == _CAMERA_MATRIX_DATA_NP

    def test_project(self):
        cameramatrix = CM(_CAMERA_MATRIX_DATA)
        with pytest.raises(TypeError):
            cameramatrix.project([])
        with pytest.raises(TypeError):
            cameramatrix.project([1])
        with pytest.raises(TypeError):
            cameramatrix.project([1, 1, 1, 1])
        with pytest.raises(ZeroDivisionError):
            cameramatrix.project([0, 0, 0])

        assert cameramatrix.project([0, 0]) == Vector2D(4, 7)
        assert cameramatrix.project([0.0, 0.0]) == Vector2D(4.0, 7.0)
        assert cameramatrix.project([1, 2]) == Vector2D(12, 19)
        assert cameramatrix.project([1, 2, 3]) == Vector2D(6.666666666666666, 11.0)


class TestDistortionCoefficients:
    def test__init__(self):
        with pytest.raises(TypeError):
            DistortionCoefficients(k1=0.0)
        with pytest.raises(TypeError):
            DistortionCoefficients(p1=0.0)
        with pytest.raises(TypeError):
            DistortionCoefficients(p1=0.0, k2=0.0)
        with pytest.raises(TypeError):
            DistortionCoefficients(p2=0.0, k1=0.0)
        with pytest.raises(TypeError):
            DistortionCoefficients(p2=0.0, k2=0.0)

        assert DistortionCoefficients(p1=0.0, k1=0.0)

    def test__distortion_generator(self):
        test_value_p = [("p1", 1.0), ("p2", 2.0)]
        test_value_k = [("k1", 1.0), ("k2", 2.0)]
        distortion_generator_with_p = DistortionCoefficients._distortion_generator(
            "p", _DISTORTIONCOEFFICIENTS_DATA
        )
        for value in distortion_generator_with_p:
            assert value in test_value_p

        distortion_generator_with_k = DistortionCoefficients._distortion_generator(
            "k", _DISTORTIONCOEFFICIENTS_DATA
        )
        for value in distortion_generator_with_k:
            assert value in test_value_k

    def test__repr_attrs(self):
        pass

    def test__calculate_radial_distortion(self):
        DC = DistortionCoefficients(p1=1.0, k1=2.0)
        radial_distortion_fisheye_true = DC._calculate_radial_distortion(r2=1.0, is_fisheye=True)
        radial_distortion_fisheye_false = DC._calculate_radial_distortion(r2=1.0, is_fisheye=False)

        assert radial_distortion_fisheye_true == 1.7543443096568176
        assert radial_distortion_fisheye_false == 3.0

    def test__calculate_tangential_distortion(self):
        dc_with_p1_p2 = DistortionCoefficients(p1=1.0, p2=2.0, k1=1.0)
        with pytest.raises(AttributeError):
            dc_p1_only = DistortionCoefficients(p1=1.0, k1=1.0)
            dc_p1_only_fisheye_false = dc_p1_only._calculate_tangential_distortion(
                r2=1.0, x2=2.0, y2=3.0, xy2=4.0, is_fisheye=False
            )
        with pytest.raises(TypeError):
            dc_p2_only = DistortionCoefficients(p2=1.0, k1=1.0)
            dc_p2_only_fisheye_false = dc_p1_only._calculate_tangential_distortion(
                r2=1.0, x2=2.0, y2=3.0, xy2=4.0, is_fisheye=False
            )

        fisheye_true_1 = dc_with_p1_p2._calculate_tangential_distortion(
            r2=1.0, x2=2.0, y2=3.0, xy2=4.0, is_fisheye=True
        )
        fisheye_true_2 = dc_with_p1_p2._calculate_tangential_distortion(1.0, 2.0, 3.0, 4.0, True)
        fisheye_true_3 = dc_p1_only._calculate_tangential_distortion(1.0, 2.0, 3.0, 4.0, True)

        fisheye_false_1 = dc_with_p1_p2._calculate_tangential_distortion(
            r2=1.0, x2=2.0, y2=3.0, xy2=4.0, is_fisheye=False
        )
        fisheye_false_2 = dc_with_p1_p2._calculate_tangential_distortion(1.0, 2.0, 3.0, 4.0, False)

        assert fisheye_true_1 == (0.0, 0.0)
        assert fisheye_true_1 == fisheye_true_2
        assert fisheye_true_2 == fisheye_true_3

        assert fisheye_false_1 == (14.0, 15.0)
        assert fisheye_false_1 == fisheye_false_2

    def test__list_distortions(self):
        DC = DistortionCoefficients(p1=1.0, p2=2.0, k1=3.0, k2=4.0)
        list_with_p = DC._list_distortions("p")
        list_with_k = DC._list_distortions("k")

        for value in list_with_p:
            assert value in [1.0, 2.0]

        for value in list_with_k:
            assert value in [3.0, 4.0]

    def test_loads_and_dumps(self):
        DC = DistortionCoefficients.loads(_DISTORTIONCOEFFICIENTS_DATA)
        assert DC.dumps() == _DISTORTIONCOEFFICIENTS_DATA

    def test_distort(self):
        DC = DistortionCoefficients(p1=1.0, p2=2.0, k1=3.0, k2=4.0)
        with pytest.raises(TypeError):
            DC.distort((1.0, 2.0), True)
        with pytest.raises(TypeError):
            DC.distort((1.0, 2.0, 3.0, 4.0), is_fisheye=True)

        distored_2d_fisheye_true_1 = DC.distort((1.0, 2.0), is_fisheye=True)
        distored_2d_fisheye_true_2 = DC.distort((1.0, 2.0, 3.0), is_fisheye=True)

        distored_2d_fisheye_false_1 = DC.distort((1.0, 2.0), is_fisheye=False)
        distored_2d_fisheye_false_2 = DC.distort((1.0, 2.0, 3.0), is_fisheye=False)

        assert distored_2d_fisheye_true_1 == Vector2D(6.158401093771876, 12.316802187543752)
        assert distored_2d_fisheye_true_2 == Vector2D(0.83187700005734, 1.66375400011468)
        assert distored_2d_fisheye_false_1 == Vector2D(134.0, 253.0)
        assert distored_2d_fisheye_false_2 == Vector2D(3.3004115226337447, 4.934156378600823)


class TestCameraIntrinsics:
    def test__init__(self):
        with pytest.raises(TypeError):
            CI(p1=0, p2=0, k1=0, k2=0)

        cameraintrinsics_matrix = CI(_CAMERA_MATRIX_DATA, p1=1, p2=2, k1=1, k2=2)
        cameraintrinsics_values = CI(fx=0, fy=0, cx=0, cy=0, p1=0, p2=0, k1=0, k2=0)

    def test_loads_and_dumps(self):
        cameraintrinsics = CI.loads(_CAMERAINTRINSICS_DATA)
        assert cameraintrinsics.dumps() == _CAMERAINTRINSICS_DATA

    def test_camera_matrix(self):
        cameraintrinsics_matrix = CI(_CAMERA_MATRIX_DATA, p1=1, p2=2, k1=1, k2=2)
        CI_camera_matrix = cameraintrinsics_matrix.camera_matrix

        camera_matrix = CM(_CAMERA_MATRIX_DATA)

    def test_distortion_coefficients(self):
        cameraintrinsics_values = CI(fx=1, fy=2, cx=3, cy=4, p1=1, p2=2, k1=1, k2=2)
        CI_distortion_coefficients = cameraintrinsics_values.distortion_coefficients
        distortion_coefficients = DistortionCoefficients(p1=1, p2=2, k1=1, k2=2)

    def test_set_camera_matrix(self):
        init_camera_intrinstic = CI(fx=0, fy=0, cx=0, cy=0, p1=0, p2=0, k1=0, k2=0)
        init_camera_intrinstic.set_camera_matrix(fx=2, fy=6, cx=4, cy=7, skew=3)
        set_camera_matrix = init_camera_intrinstic.camera_matrix

        camera_matrix = CM(fx=2, fy=6, cx=4, cy=7, skew=3)

    def test_set_distortion_coefficients(self):
        init_distortion_coefficients = CI(fx=0, fy=0, cx=0, cy=0, p1=0, p2=0, k1=0, k2=0)
        init_distortion_coefficients.set_distortion_coefficients(p1=1, p2=2, k1=1, k2=2)
        set_distortion_coefficients_1 = init_distortion_coefficients.distortion_coefficients

    def test_project(self):
        # camera_intrinsics = CI(fx=1, fy=2, cx=3, cy=4, p1=1, p2=2, k1=1, k2=2)
        # cameraintrinsics = camera_intrinsics.project((1.0, 2.0), is_fisheye=True)
        pass
