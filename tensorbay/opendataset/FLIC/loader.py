#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the FLIC Dataloader"""

import os
from typing import Any, Dict, Iterator, Tuple

from ...dataset import Data, Dataset
from ...label import Classification, LabeledBox2D, LabeledKeypoints2D

DATASET_NAME = "FLIC"
_VALID_KEYPOINT_INDICES = [0, 1, 2, 3, 4, 5, 6, 9, 12, 13, 16]


def FLIC(path: str) -> Dataset:
    """FLIC open dataset dataloader.

    :param path: Path to FLIC
    The folder structure should be like:
    <path>
        exampls.mat
        images/
            2-fast-2-furious-00003571.jpg
            ...
    :return: loaded FLIC Dataset
    """
    from scipy.io import loadmat  # pylint: disable=import-outside-toplevel

    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)

    annotations = loadmat(os.path.join(root_path, "examples.mat"))["examples"][0]
    dataset.create_segment("train")
    dataset.create_segment("test")
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    # try whether the dataset has bad segment
    try:
        _ = annotations["isbad"]
        flag = True
        dataset.create_segment("bad")
        dataset.catalog.classification.add_attribute(name="isunchecked", type_="boolean")
    except ValueError:
        flag = False

    for data, segment_name in _get_data(root_path, annotations, flag):
        dataset.get_segment_by_name(segment_name).append(data)

    return dataset


def _get_data(path: str, annotations: Any, flag: bool) -> Iterator[Tuple[Data, str]]:
    filepath_to_data: Dict[str, Data] = {}

    for annotation in annotations:
        filepath = annotation["filepath"][0]

        keypoints = LabeledKeypoints2D(
            annotation["coords"].T[_VALID_KEYPOINT_INDICES],
            attributes={"poselet_hit_idx": annotation["poselet_hit_idx"].T.tolist()},
        )
        box2d = LabeledBox2D(annotation["torsobox"][0].tolist())

        if filepath not in filepath_to_data:
            data = Data(os.path.join(path, "images", filepath))
            data.labels.keypoints2d = [keypoints]
            data.labels.box2d = [box2d]
            attribute = {"currframe": int(annotation["currframe"][0][0])}

            if flag:
                attribute["isunchecked"] = bool(annotation["isunchecked"])
            data.labels.classification = Classification(
                category=annotation["moviename"][0], attributes=attribute
            )
            filepath_to_data[filepath] = data

            if annotation["istrain"]:
                segment_name = "train"
            elif annotation["istest"]:
                segment_name = "test"
            else:
                segment_name = "bad"
            yield data, segment_name

        else:
            image_data = filepath_to_data[filepath]
            image_data.labels.keypoints2d.append(keypoints)
            image_data.labels.box2d.append(box2d)
