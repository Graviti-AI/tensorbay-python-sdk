#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file handles with the DownsampledImagenet dataset"""

import os

from ...dataset import Data, Dataset, Segment
from .._utility import glob

DATASET_NAME = "DownsampledImagenet"
SEGMENT_NAMES = ["train_32x32", "train_64x64", "valid_32x32", "valid_64x64"]


def DownsampledImagenet(path: str) -> Dataset:
    """
    DownsampledImagenet open dataset dataloader

    :param path: Path to DownsampledImagenet dataset
    the file structure should be like:
    <path>
        valid_32x32/
            <imagename>.png
            ...
        valid_64x64/
            <imagename>.png
            ...
        train_32x32/
            <imagename>.png
            ...
        train_64x64/
            <imagename>.png
            ...

    :return: load `Dataset` object
    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)

    for segment_name in SEGMENT_NAMES:
        dataset.add_segment(_get_segment(segment_name, root_path))
    return dataset


def _get_segment(path: str, segment_name: str) -> Segment:
    segment = Segment(segment_name)
    image_paths = glob(os.path.join(path, segment_name, "*.png"))

    for image_path in image_paths:
        segment.append(Data(image_path))
    return segment
