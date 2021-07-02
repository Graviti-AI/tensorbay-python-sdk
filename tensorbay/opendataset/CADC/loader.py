#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import quaternion

from ...dataset import Data, Frame, FusionDataset
from ...exception import ModuleImportError
from ...label import LabeledBox3D
from ...sensor import Camera, Lidar, Sensors
from .._utility import glob

DATASET_NAME = "CADC"


def CADC(path: str) -> FusionDataset:
    """Dataloader of the `CADC`_ dataset.

    .. _CADC: http://cadcd.uwaterloo.ca/index.html

    The file structure should be like::

        <path>
            2018_03_06/
                0001/
                    3d_ann.json
                    labeled/
                        image_00/
                            data/
                                0000000000.png
                                0000000001.png
                                ...
                            timestamps.txt
                        ...
                        image_07/
                            data/
                            timestamps.txt
                        lidar_points/
                            data/
                            timestamps.txt
                        novatel/
                            data/
                            dataformat.txt
                            timestamps.txt
                ...
                0018/
                calib/
                    00.yaml
                    01.yaml
                    02.yaml
                    03.yaml
                    04.yaml
                    05.yaml
                    06.yaml
                    07.yaml
                    extrinsics.yaml
                    README.txt
            2018_03_07/
            2019_02_27/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded `~tensorbay.dataset.dataset.FusionDataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = FusionDataset(DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for date in os.listdir(root_path):
        date_path = os.path.join(root_path, date)
        sensors = _load_sensors(os.path.join(date_path, "calib"))
        for index in os.listdir(date_path):
            if index == "calib":
                continue

            segment = dataset.create_segment(f"{date}-{index}")
            segment.sensors = sensors
            segment_path = os.path.join(root_path, date, index)
            data_path = os.path.join(segment_path, "labeled")

            with open(os.path.join(segment_path, "3d_ann.json"), "r") as fp:
                # The first line of the json file is the json body.
                annotations = json.loads(fp.readline())
            timestamps = _load_timestamps(sensors, data_path)
            for frame_index, annotation in enumerate(annotations):
                segment.append(_load_frame(sensors, data_path, frame_index, annotation, timestamps))

    return dataset


def _load_timestamps(sensors: Sensors, data_path: str) -> Dict[str, List[str]]:
    timestamps = {}
    for sensor_name in sensors.keys():
        data_folder = f"image_{sensor_name[-2:]}" if sensor_name != "LIDAR" else "lidar_points"
        timestamp_file = os.path.join(data_path, data_folder, "timestamps.txt")
        with open(timestamp_file, "r") as fp:
            timestamps[sensor_name] = fp.readlines()

    return timestamps


def _load_frame(
    sensors: Sensors,
    data_path: str,
    frame_index: int,
    annotation: Dict[str, Any],
    timestamps: Dict[str, List[str]],
) -> Frame:
    frame = Frame()
    for sensor_name in sensors.keys():
        # The data file name is a string of length 10 with each digit being a number:
        # 0000000000.jpg
        # 0000000001.bin
        data_file_name = f"{frame_index:010}"

        # Each line of the timestamps file looks like:
        # 2018-03-06 15:02:33.000000000
        timestamp = datetime.strptime(
            timestamps[sensor_name][frame_index][:23], "%Y-%m-%d %H:%M:%S.%f"
        ).timestamp()
        if sensor_name != "LIDAR":
            # The image folder corresponds to different cameras, whose name is likes "CAM00".
            # The image folder looks like "image_00".
            camera_folder = f"image_{sensor_name[-2:]}"
            image_file = f"{data_file_name}.png"

            data = Data(
                os.path.join(data_path, camera_folder, "data", image_file),
                target_remote_path=f"{camera_folder}-{image_file}",
                timestamp=timestamp,
            )
        else:
            data = Data(
                os.path.join(data_path, "lidar_points", "data", f"{data_file_name}.bin"),
                timestamp=timestamp,
            )
            data.label.box3d = _load_labels(annotation["cuboids"])

        frame[sensor_name] = data
    return frame


def _load_labels(boxes: List[Dict[str, Any]]) -> List[LabeledBox3D]:
    labels = []
    for box in boxes:
        dimension = box["dimensions"]
        position = box["position"]

        attributes = box["attributes"]
        attributes["stationary"] = box["stationary"]
        attributes["camera_used"] = box["camera_used"]
        attributes["points_count"] = box["points_count"]

        label = LabeledBox3D(
            size=(
                dimension["y"],  # The "y" dimension is the width from front to back.
                dimension["x"],  # The "x" dimension is the width from left to right.
                dimension["z"],
            ),
            translation=(
                position["x"],  # "x" axis points to the forward facing direction of the object.
                position["y"],  # "y" axis points to the left direction of the object.
                position["z"],
            ),
            rotation=quaternion.from_rotation_vector((0, 0, box["yaw"])),
            category=box["label"],
            attributes=attributes,
            instance=box["uuid"],
        )
        labels.append(label)

    return labels


def _load_sensors(calib_path: str) -> Sensors:
    try:
        import yaml  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name, "pyyaml") from error  # type: ignore[arg-type]

    sensors = Sensors()

    lidar = Lidar("LIDAR")
    lidar.set_extrinsics()
    sensors.add(lidar)

    with open(os.path.join(calib_path, "extrinsics.yaml"), "r") as fp:
        extrinsics = yaml.load(fp, Loader=yaml.FullLoader)

    for camera_calibration_file in glob(os.path.join(calib_path, "[0-9]*.yaml")):
        with open(camera_calibration_file, "r") as fp:
            camera_calibration = yaml.load(fp, Loader=yaml.FullLoader)

        # camera_calibration_file looks like:
        # /path-to-CADC/2018_03_06/calib/00.yaml
        camera_name = f"CAM{os.path.splitext(os.path.basename(camera_calibration_file))[0]}"
        camera = Camera(camera_name)
        camera.description = camera_calibration["camera_name"]

        camera.set_extrinsics(matrix=extrinsics[f"T_LIDAR_{camera_name}"])

        camera_matrix = camera_calibration["camera_matrix"]["data"]
        camera.set_camera_matrix(matrix=[camera_matrix[:3], camera_matrix[3:6], camera_matrix[6:9]])

        distortion = camera_calibration["distortion_coefficients"]["data"]
        camera.set_distortion_coefficients(**dict(zip(("k1", "k2", "p1", "p2", "k3"), distortion)))

        sensors.add(camera)
    return sensors
