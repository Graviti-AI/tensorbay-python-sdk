#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file define HeadPoseImage Dataloader"""

import os
import re
from itertools import islice
from typing import Dict, Tuple

from ...dataset import Data, Dataset
from ...label import LabeledBox2D
from .._utility import glob

DATASET_NAME = "Head Pose Image"


def HeadPoseImage(path: str) -> Dataset:
    """Load the Head Pose Image Dataset to TensorBay

    :param path: the root directory of the dataset
    The file structure should be like:
    <path>
        Person01/
            person01100-90+0.jpg
            person01100-90+0.txt
            person01101-60-90.jpg
            person01101-60-90.txt
            ...
        Person02/
        Person03/
        ...
        Person15/

    :return: a loaded dataset
    """

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()
    image_paths = glob(os.path.join(path, "Person*", "*.jpg"))

    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        data = Data(image_path)
        data.labels.box2d = [
            LabeledBox2D(
                _load_label_box(image_path.replace("jpg", "txt")),
                category=image_name[6:8],
                attributes=_load_attributes(image_name),
            )
        ]
        segment.append(data)
    return dataset


def _load_attributes(image_name: str) -> Dict[str, int]:
    serie = image_name[8]
    number = image_name[9:11]
    tilt, pan = re.findall(r"[\+\-]\d+", image_name)
    attributes = {
        "Serie": int(serie),
        "Number": int(number),
        "Vertical angle": int(tilt),
        "Horizontal angle": int(pan),
    }
    return attributes


def _load_label_box(label_file_path: str) -> Tuple[float, float, float, float]:
    with open(label_file_path) as fp:
        center_x, center_y, width, height = map(int, islice(fp, 3, 7))
    return (
        center_x - width / 2,
        center_y - height / 2,
        center_x + width / 2,
        center_y + height / 2,
    )
