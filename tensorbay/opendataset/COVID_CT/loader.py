#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...label import Classification

DATASET_NAME = "COVID_CT"
_SEGMENT_TO_PATH = {
    "test_COVID": ("testCT_COVID.txt", "CT_COVID", "COVID"),
    "train_COVID": ("trainCT_COVID.txt", "CT_COVID", "COVID"),
    "val_COVID": ("valCT_COVID.txt", "CT_COVID", "COVID"),
    "test_NonCOVID": ("testCT_NonCOVID.txt", "CT_NonCOVID", "NonCOVID"),
    "train_NonCOVID": ("trainCT_NonCOVID.txt", "CT_NonCOVID", "NonCOVID"),
    "val_NonCOVID": ("valCT_NonCOVID.txt", "CT_NonCOVID", "NonCOVID"),
}


def COVID_CT(path: str) -> Dataset:
    """Dataloader of the `COVID-CT`_ dataset.

    .. _COVID-CT: https://github.com/UCSD-AI4H/COVID-CT

    The file structure should be like::

        <path>
            Data-split/
                COVID/
                    testCT_COVID.txt
                    trainCT_COVID.txt
                    valCT_COVID.txt
                NonCOVID/
                    testCT_NonCOVID.txt
                    trainCT_NonCOVID.txt
                    valCT_NonCOVID.txt
            Images-processed/
                CT_COVID/
                    ...
                    2020.01.24.919183-p27-132.png
                    2020.01.24.919183-p27-133.png
                    ...
                    PIIS0140673620303603%8.png
                    ...
                CT_NonCOVID/
                    0.jpg
                    1%0.jog
                    ...
                    91%1.jpg
                    102.png
                    ...
                    2341.png

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.
    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    data_split_path = os.path.join(root_path, "Data-split")
    images_processed_path = os.path.join(root_path, "Images-processed")

    for segment_name, (split_filename, image_directory, category) in _SEGMENT_TO_PATH.items():
        segment = dataset.create_segment(segment_name)
        image_directory = os.path.join(images_processed_path, image_directory)
        with open(os.path.join(data_split_path, category, split_filename), "r") as fp:
            for line in fp:
                image_path = os.path.join(image_directory, line.strip("\n"))
                data = Data(image_path)
                data.label.classification = Classification(category)
                segment.append(data)

    return dataset
