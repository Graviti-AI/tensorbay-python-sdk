#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from typing import Dict, List

from ...dataset import Data, Dataset
from ...label import Classification, LabeledBox2D
from .._utility import glob

SEGMENT_LIST = ["train", "val", "test"]
DATASET_NAME = "JHU-CROWD"
_OCCLUSION_MAP = {1: "visible", 2: "partial-occlusion", 3: "full-occlusion"}
_WEATHER_CONDITION_MAP = {0: "no weather degradationi", 1: "fog/haze", 2: "rain", 3: "snow"}


def JHU_CROWD(path: str) -> Dataset:
    """Dataloader of the `JHU-CROWD++`_ dataset.

    .. _JHU-CROWD++: http://www.crowd-counting.com/

    The file structure should be like::

        <path>
            train/
                images/
                    0000.jpg
                    ...
                gt/
                    0000.txt
                    ...
                image_labels.txt
            test/
            val/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    for segment_name in SEGMENT_LIST:
        segment = dataset.create_segment(segment_name)
        segment_path = os.path.join(path, segment_name)
        image_root_path = os.path.join(segment_path, "images")
        image_paths = glob(os.path.join(image_root_path, "*.jpg"))

        image_labels = _load_image_labels(os.path.join(segment_path, "image_labels.txt"))
        for image_path in image_paths:
            data = Data(image_path)
            image_file = os.path.basename(image_path)
            label_file = image_file.replace("jpg", "txt")
            data.label.box2d = _load_box_labels(os.path.join(segment_path, "gt", label_file))
            data.label.classification = image_labels[os.path.splitext(image_file)[0]]
            segment.append(data)
    return dataset


def _load_box_labels(file_path: str) -> List[LabeledBox2D]:
    box_labels = []
    with open(file_path, encoding="utf-8") as fp:
        for line in fp:
            center_x, center_y, width, height, occlusion, blur = map(int, line.strip().split())
            attributes = {"occlusion-level": _OCCLUSION_MAP[occlusion], "blur-level": bool(blur)}
            box_labels.append(
                LabeledBox2D.from_xywh(
                    x=center_x - width / 2,
                    y=center_y - height / 2,
                    width=width,
                    height=height,
                    attributes=attributes,
                )
            )
    return box_labels


def _load_image_labels(file_path: str) -> Dict[str, Classification]:
    with open(file_path, encoding="utf-8") as fp:
        image_labels = {}
        for line in fp:
            img_index, count, scene, weather, distractor = line.strip().split(",")
            attributes = {
                "total-count": int(count),
                "scene-type": scene,
                "weather-condition": _WEATHER_CONDITION_MAP[int(weather)],
                "distractor": bool(int(distractor)),
            }
            image_labels[img_index] = Classification(attributes=attributes)
    return image_labels
