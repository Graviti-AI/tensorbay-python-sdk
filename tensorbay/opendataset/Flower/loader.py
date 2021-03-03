#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the 17 Category Flower dataset and the 102 Category Flower dataset."""

import os

from ...dataset import Data, Dataset
from ...label import Classification

DATASET_NAME_17 = "17 Category Flower"
DATASET_NAME_102 = "102 Category Flower"
_SEGMENT_NAMES_17 = {"train": "trn1", "validation": "val1", "test": "tst1"}
_SEGMENT_NAMES_102 = {"train": "trnid", "validation": "valid", "test": "tstid"}


def Flower17(path: str) -> Dataset:
    """Dataloader of the 17 Category Flower dataset.

    The dataset are 3 separate splits.
    The results in the paper are averaged over the 3 splits.
    We just use (trn1, val1, tst1) to split it.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    jpg/
                        image_0001.jpg
                        ...
                    datasplits.mat

    Returns:
        A loaded dataset.

    """
    from scipy.io import loadmat  # pylint: disable=import-outside-toplevel

    root_path = os.path.abspath(os.path.expanduser(path))
    segment_info = loadmat(os.path.join(root_path, "datasplits.mat"))

    dataset = Dataset(DATASET_NAME_17)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_17.json"))
    categories = list(dataset.catalog.classification.categories)
    for key, value in _SEGMENT_NAMES_17.items():
        segment = dataset.create_segment(key)
        segment_info[value][0].sort()
        for index in segment_info[value][0]:
            data = Data(os.path.join(root_path, "jpg", f"image_{index:04d}.jpg"))

            # There are 80 images for each category
            data.label.classification = Classification(category=categories[(index - 1) // 80])
            segment.append(data)

    return dataset


def Flower102(path: str) -> Dataset:
    """Dataloader of the 102 Category Flower dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    jpg/
                        image_00001.jpg
                        ...
                    imagelabels.mat
                    setid.mat

    Returns:
        A loaded dataset.

    """
    from scipy.io import loadmat  # pylint: disable=import-outside-toplevel

    root_path = os.path.abspath(os.path.expanduser(path))
    labels = loadmat(os.path.join(root_path, "imagelabels.mat"))["labels"][0]
    segment_info = loadmat(os.path.join(root_path, "setid.mat"))

    dataset = Dataset(DATASET_NAME_102)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_102.json"))
    categories = list(dataset.catalog.classification.categories)
    for key, value in _SEGMENT_NAMES_102.items():
        segment = dataset.create_segment(key)
        segment_info[value][0].sort()
        for index in segment_info[value][0]:
            data = Data(os.path.join(root_path, "jpg", f"image_{index:05d}.jpg"))
            data.label.classification = Classification(categories[int(labels[index - 1]) - 1])
            segment.append(data)
    return dataset
