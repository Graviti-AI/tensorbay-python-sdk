#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of LIP dataset."""

import csv
import os
from itertools import islice
from typing import List

from tensorbay.dataset import Data, Dataset
from tensorbay.geometry import Keypoint2D
from tensorbay.label import LabeledKeypoints2D, SemanticMask
from tensorbay.utility import chunked

DATASET_NAME = "LIP"
_SEGMENT_NAMES = ("train", "val", "test")


def LIP(path: str) -> Dataset:
    """`LIP <https://github.com/Engineering-Course/LIP_SSL>`_ dataset.

    The file structure should be like::

        <path>
            Testing_images/
                testing_images/
                    315_462476.jpg
                    ...
                test_id.txt
            TrainVal_images/
                TrainVal_images/
                    train_images/
                        77_471474.jpg
                        ...
                    val_images/
                        36_453991.jpg
                        ...
                train_id.txt
                val_id.txt
            TrainVal_parsing_annotations/
                TrainVal_parsing_annotations/
                    train_segmentations/
                        77_471474.png
                        ...
                    val_segmentations/
                        36_453991.png
                        ...
            TrainVal_pose_annotations/
                lip_train_set.csv
                lip_val_set.csv

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    test_path = os.path.join(root_path, "Testing_images")
    trainval_image_path = os.path.join(root_path, "TrainVal_images", "TrainVal_images")
    trainval_parsing_path = os.path.join(
        root_path, "TrainVal_parsing_annotations", "TrainVal_parsing_annotations"
    )
    pose_path = os.path.join(root_path, "TrainVal_pose_annotations")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        if segment_name == "test":
            image_path = os.path.join(test_path, "testing_images")
            with open(os.path.join(test_path, "test_id.txt"), encoding="utf-8") as fp:
                for stem in fp:
                    segment.append(Data(os.path.join(image_path, f"{stem.rstrip()}.jpg")))
        else:
            image_path = os.path.join(trainval_image_path, f"{segment_name}_images")
            parsing_path = os.path.join(trainval_parsing_path, f"{segment_name}_segmentations")
            with open(
                os.path.join(pose_path, f"lip_{segment_name}_set.csv"), encoding="utf-8"
            ) as csvfile:
                for keypoints_info in csv.reader(csvfile):
                    segment.append(_get_data(keypoints_info, image_path, parsing_path))
    return dataset


def _get_data(keypoints_info: List[str], image_path: str, parsing_path: str) -> Data:
    stem = os.path.splitext(keypoints_info[0])[0]
    data = Data(os.path.join(image_path, f"{stem}.jpg"))
    label = data.label
    label.semantic_mask = SemanticMask(os.path.join(parsing_path, f"{stem}.png"))
    keypoints = LabeledKeypoints2D()
    for x, y, v in chunked(islice(keypoints_info, 1, None), 3):
        keypoints.append(
            Keypoint2D(float(x), float(y), 1 - int(v)) if x.isnumeric() else Keypoint2D(0, 0, 0)
        )
    label.keypoints2d = [keypoints]
    return data
