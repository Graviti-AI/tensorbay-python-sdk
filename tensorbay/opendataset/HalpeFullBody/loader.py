#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import json
import os
from typing import Any, Dict

from ...dataset import Data, Dataset
from ...geometry import Keypoint2D
from ...label import LabeledKeypoints2D
from ...utility import chunked

DATASET_NAME = "HalpeFullBody"

_SEGMENT_SPLIT = (
    ("train", "halpe_train_v1.json", os.path.join("hico_20160224_det", "images", "train2015")),
    ("val", "halpe_val_v1.json", "val2017"),
)


def HalpeFullBody(path: str) -> Dataset:
    """Dataloader of the `Halpe Full-Body Human Keypoints and HOI-Det`_ dataset.

    .. _Halpe Full-Body Human Keypoints and HOI-Det: https://github.com/Fang-Haoshu/Halpe-FullBody/ # noqa: E501

    The folder structure should be like::

        <path>
            halpe_train_v1.json
            halpe_val_v1.json
            hico_20160224_det/
                images/
                    train2015/
                        HICO_train2015_00000001.jpg
                        ...
            val2017/
                000000000139.jpg
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for mode, label_file, image_directory in _SEGMENT_SPLIT:
        segment = dataset.create_segment(mode)

        with open(os.path.join(root_path, label_file), "r", encoding="utf-8") as fp:
            annotations = json.load(fp)

        if mode == "train":
            for annotation, image in zip(annotations["annotations"], annotations["images"]):
                image_path = os.path.join(root_path, image_directory, image["file_name"])
                segment.append(_get_data(image_path, annotation))
        else:
            for annotation in annotations["annotations"]:
                image_path = os.path.join(
                    root_path, image_directory, f"{annotation['image_id']:012}.jpg"
                )
                segment.append(_get_data(image_path, annotation))

    return dataset


def _get_data(image_path: str, annotation: Dict[str, Any]) -> Data:
    data = Data(image_path)

    keypoints = LabeledKeypoints2D()
    for x, y, v in chunked(annotation["keypoints"], 3):
        keypoints.append(Keypoint2D(x, y, v if v in (0, 1, 2) else 2))  # pylint: disable=no-member

    data.label.keypoints2d = [keypoints]

    return data
