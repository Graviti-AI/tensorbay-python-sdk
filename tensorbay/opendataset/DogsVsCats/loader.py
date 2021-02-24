#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the DogsVsCats dataloader."""

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "Dogs vs. Cats"
_SEGMENTS = {"train": True, "test": False}


def DogsVsCats(path: str) -> Dataset:
    """Open dataset DogsVsCats dataloader.

    The file structure should be like::

        <path>
            train/
                cat.0.jpg
                ...
                dog.0.jpg
                ...
            test/
                1000.jpg
                1001.jpg
                ...

    Arguments:
        path: Path to DogsVsCats dataset.

    Returns:
        Dataset: Loaded ``Dataset`` object.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name, is_labeled in _SEGMENTS.items():
        segment = dataset.create_segment(segment_name)
        image_paths = glob(os.path.join(root_path, segment_name, "*.jpg"))
        for image_path in image_paths:
            data = Data(image_path)
            if is_labeled:
                data.labels.classification = Classification(os.path.basename(image_path)[:3])
            segment.append(data)

    return dataset
