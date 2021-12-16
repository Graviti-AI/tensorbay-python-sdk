#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Methods for open datasets of nuScenes format."""

import json
import os
from bisect import bisect
from itertools import accumulate
from typing import Any, Dict, List, Union

from tensorbay.sensor import Camera, Lidar, Radar

_SENSOR_TYPE_CLASS = {
    "lidar": Lidar,
    "radar": Radar,
    "camera": Camera,
}


def get_info_with_token(info_path: str, annotation_part: str) -> Dict[str, Any]:
    """Parse the nuScenes format label files.

    Arguments:
        info_path: The path of the JSON files.
        annotation_part: The name of JSON file.

    Returns:
        An annotation dict whose keys are tokens.

    """
    filepath = os.path.join(info_path, f"{annotation_part}.json")
    with open(filepath, encoding="utf-8") as fp:
        info = json.load(fp)
    return {item.pop("token"): item for item in info}


def get_info_with_determined_token(
    info_path: str,
    annotation_part: str,
    determined_token: str = "sample_token",
    no_key_frame: bool = False,
) -> Dict[str, List[Any]]:
    """Parse the nuScenes label files with determined key.

    Arguments:
        info_path: The path of JSON files.
        annotation_part: The name of JSON file.
        determined_token: The key name of the dict.
        no_key_frame: Whether need key frame.

    Returns:
        An annotation dict whose keys are determined tokens.

    """
    filepath = os.path.join(info_path, f"{annotation_part}.json")
    with open(filepath, encoding="utf-8") as fp:
        info = json.load(fp)
    info_with_keys: Dict[str, List[Any]] = {}
    for item in info:
        if no_key_frame or item["is_key_frame"]:
            info_with_keys.setdefault(item.pop(determined_token), []).append(item)
    return info_with_keys


def uncompress_rle(original_code: str) -> List[int]:
    """Uncompress function for RLE of coco API.

    Source Code: https://github.com/cocodataset/cocoapi/blob/master/common/maskApi.c#L218

    Arguments:
        original_code: The original ASCII code.

    Returns:
        The uncompressed RLE.

    """
    pointer = 0
    rle: List[int] = []
    m = 0
    while pointer < len(original_code):
        x = 0
        k = 0
        more = 1
        while more:
            char = ord(original_code[pointer]) - 48
            x |= (char & 0x1F) << 5 * k
            more = char & 0x20
            pointer += 1
            k += 1
            if not more and (char & 0x10):
                x |= -1 << 5 * k
        if m > 2:
            x += rle[m - 2]
        rle.append(x)
        m += 1
    return rle


def transpose_rle(rle: List[int], height: int, width: int) -> List[int]:
    """Transpose function for uncompressed RLE.

    Arguments:
        rle: The original RLE.
        height: The height of mask.
        width: The width of mask.

    Returns:
        RLE which has been transposed.

    """
    accumulate_values = list(accumulate(rle))
    flag = 0
    count = 0
    rle = []
    for i in range(height):
        for index in range(i, i + height * width, height):
            if bisect(accumulate_values, index) % 2 == flag:
                count += 1
                continue
            flag = 1 - flag
            rle.append(count)
            count = 1
    rle.append(count)
    return rle


def get_sensor(
    sensor_type: str,
    sensor_name: str,
    calibrated_sensor_info: Dict[str, Any],
) -> Union[Camera, Lidar, Radar]:
    """Load the sensor information for the fusion segment.

    Arguments:
        sensor_type: The type of the sensor.
        sensor_name: The name of the sensor.
        calibrated_sensor_info: The information of the sensor.

    Returns:
        The sensor information of the fusion segment.

    """
    sensor = _SENSOR_TYPE_CLASS[sensor_type](sensor_name)
    sensor.set_extrinsics(
        translation=calibrated_sensor_info["translation"],
        rotation=calibrated_sensor_info["rotation"],
    )
    intrinsics = calibrated_sensor_info["camera_intrinsic"]
    if intrinsics:
        sensor.set_camera_matrix(matrix=intrinsics)  # type: ignore[attr-defined]
        distortion = calibrated_sensor_info.get("camera_distortion", None)
        if distortion:
            distortion_keys = ("k1", "k2", "p1", "p2", "k3", "k4")
            kwargs = dict(zip(distortion_keys, distortion))
            sensor.set_distortion_coefficients(**kwargs)  # type: ignore[attr-defined]
    return sensor  # type: ignore[return-value]
