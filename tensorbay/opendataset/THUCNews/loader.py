#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of THUCNews dataset."""

import os

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification
from tensorbay.opendataset._utility import glob

DATASET_NAME = "THUCNews"


def THUCNews(path: str) -> Dataset:
    """`THUCNews <http://thuctc.thunlp.org/>`_ dataset.

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

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    for category in dataset.catalog.classification.categories.keys():
        text_paths = glob(os.path.join(root_path, category, "*.txt"))
        for text_path in text_paths:
            data = Data(text_path)
            data.label.classification = Classification(category)

            segment.append(data)

    return dataset
