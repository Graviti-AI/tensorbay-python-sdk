#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""This files defines dataloader of THUCNews."""

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "THUCNews"


def THUCNews(path: str) -> Dataset:
    """Load the THUCNews Dataset to TensorBay

    Arguments:
        path: Path to THUCNews
            The folder structure should be like::

                <path>
                    <category>/
                        0.txt
                        1.txt
                        2.txt
                        3.txt
                        ...
                    <category>/
                    ...

    Returns:
        Loaded `Dataset` object
        
    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    categories = dataset.catalog.classification.categories
    for category in categories:
        text_paths = glob(os.path.join(root_path, category, "*.txt"))
        for text_path in text_paths:
            data = Data(text_path)
            data.labels.classification = Classification(category)

            segment.append(data)

    return dataset
