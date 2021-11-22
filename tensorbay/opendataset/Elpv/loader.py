#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of Elpv dataset."""

import os

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification

DATASET_NAME = "Elpv"


def Elpv(path: str) -> Dataset:
    """`elpv <https://github.com/zae-bayern/elpv-dataset>`_ dataset.

    The file structure should be like::

        <path>
            labels.csv
            images/
                cell0001.png
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

    csv_path = os.path.join(root_path, "labels.csv")

    with open(csv_path, encoding="utf-8") as csv_file:
        for row in csv_file:
            image_name, attributes, category = row.strip().split()
            dirname, basename = image_name.split("/")
            image_path = os.path.join(root_path, dirname, basename)
            data = Data(image_path)
            data.label.classification = Classification(
                attributes={"defect probability": float(attributes)}, category=category
            )
            segment.append(data)
    return dataset
